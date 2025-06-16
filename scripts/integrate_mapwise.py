#!/usr/bin/env python3
"""
MapBench.Live - MapWise Dataset Integration Script
Converts MapWise dataset format to MapBench.Live format
"""

import argparse
import csv
import json
import shutil
from pathlib import Path
from typing import Dict, List, Any
import re


class MapWiseIntegrator:
    def __init__(self, mapwise_path: str, output_path: str = "data/tasks"):
        self.mapwise_path = Path(mapwise_path)
        self.output_path = Path(output_path)
        self.output_path.mkdir(exist_ok=True)
        
        # Map question templates to our types
        self.question_type_mapping = {
            "count": "count",
            "binary": "yes_no",
            "single": "single_answer",
            "range": "range_answer",
            "list": "list_answer"
        }
    
    def integrate_country(self, country: str, image_variant: str = "with_annotations"):
        """Integrate data from a specific country"""
        country_path = self.mapwise_path / country
        if not country_path.exists():
            print(f"Country path {country_path} not found")
            return
        
        # Load QnA data
        qna_file = country_path / "qna.csv"
        if not qna_file.exists():
            print(f"QnA file not found for {country}")
            return
        
        # Load template mappings
        template_file = self.mapwise_path / "template.csv"
        templates = self._load_templates(template_file)
        
        # Process QnA data
        with open(qna_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            # Group questions by map_id
            map_questions = {}
            for row in reader:
                map_id = row['map_id']
                if map_id not in map_questions:
                    map_questions[map_id] = []
                
                map_questions[map_id].append(row)
        
        # Process each map
        converted_count = 0
        for map_id, questions in map_questions.items():
            task_data = self._convert_map_to_task(
                country, map_id, questions, templates, image_variant
            )
            
            if task_data:
                # Save task JSON
                task_id = f"mapwise-{country}-{map_id}"
                task_file = self.output_path / f"{task_id}.json"
                
                with open(task_file, 'w') as f:
                    json.dump(task_data, f, indent=2)
                
                # Copy image file
                self._copy_map_image(country, map_id, task_id, image_variant)
                
                converted_count += 1
        
        print(f"Converted {converted_count} maps from {country}")
    
    def _load_templates(self, template_file: Path) -> Dict[int, Dict[str, str]]:
        """Load question templates"""
        templates = {}
        
        if template_file.exists():
            with open(template_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    template_no = int(row['index'])
                    templates[template_no] = {
                        'template_discrete': row.get('Discrete', ''),
                        'template_continuous': row.get('Continuous', ''),
                        'answer_type': row.get('Type', 'Single').lower()
                    }
        
        return templates
    
    def _convert_map_to_task(self, country: str, map_id: str, 
                            questions: List[Dict], templates: Dict,
                            image_variant: str) -> Dict[str, Any]:
        """Convert MapWise map data to MapBench task format"""
        
        # Load metadata if available
        metadata = self._load_map_metadata(country, map_id)
        
        # Prepare context
        context = f"Choropleth map of {country.upper()}"
        if metadata:
            if metadata.get('title'):
                context = metadata['title']
            context += f" - {metadata.get('data_type', 'Data')} visualization"
        
        # Convert questions
        converted_questions = []
        for q in questions:
            template_no = int(q.get('template_no', 0))
            template_info = templates.get(template_no, {})
            
            # Determine question type
            answer_type = template_info.get('answer_type', 'single')
            if answer_type in self.question_type_mapping:
                q_type = self.question_type_mapping[answer_type]
            else:
                q_type = "short_answer"
            
            converted_q = {
                "q": q['question'],
                "a": q['ground_truth'],
                "type": q_type
            }
            
            # Add metadata
            if 'c_or_d' in q:
                converted_q['legend_type'] = "continuous" if q['c_or_d'] == 'c' else "discrete"
            
            if q.get('relative_region') == 'True':
                converted_q['is_relative'] = True
            
            converted_questions.append(converted_q)
        
        # Create task data
        task_data = {
            "id": f"mapwise-{country}-{map_id}",
            "map_image": f"mapwise-{country}-{map_id}.png",
            "context": context,
            "type": "choropleth",
            "source": "mapwise",
            "questions": converted_questions,
            "metadata": {
                "country": country,
                "original_map_id": map_id,
                "image_variant": image_variant
            }
        }
        
        return task_data
    
    def _load_map_metadata(self, country: str, map_id: str) -> Dict[str, Any]:
        """Load map metadata from JSON file"""
        metadata_file = self.mapwise_path / country / "json_data" / f"{map_id}.json"
        
        if metadata_file.exists():
            with open(metadata_file, 'r') as f:
                return json.load(f)
        
        return {}
    
    def _copy_map_image(self, country: str, map_id: str, task_id: str, variant: str):
        """Copy map image to tasks directory"""
        # Construct source path
        image_dir = self.mapwise_path / country / "images" / variant
        
        # Try different extensions with map_ prefix
        for ext in ['.png', '.jpg', '.jpeg']:
            source_file = image_dir / f"map_{map_id}{ext}"
            if source_file.exists():
                target_file = self.output_path / f"{task_id}.png"
                shutil.copy2(source_file, target_file)
                return
        
        print(f"Warning: Image not found for {map_id} in {variant} variant")
    
    def integrate_counterfactuals(self, limit: int = 10):
        """Integrate counterfactual examples for robustness testing"""
        cf_path = self.mapwise_path / "counter_factuals"
        if not cf_path.exists():
            print("Counterfactuals directory not found")
            return
        
        cf_types = ["original", "shuffled", "jumbled", "imaginary"]
        
        for cf_type in cf_types:
            cf_type_path = cf_path / cf_type
            if not cf_type_path.exists():
                continue
            
            # Get sample of images from maps subdirectory
            maps_path = cf_type_path / "maps"
            if maps_path.exists():
                images = list(maps_path.glob("*.png"))[:limit]
            else:
                images = list(cf_type_path.glob("*.png"))[:limit]
            
            for img_path in images:
                # Extract map info from filename
                # Format: usually "{country}_{map_id}_{cf_type}.png"
                parts = img_path.stem.split('_')
                if len(parts) >= 2:
                    country = parts[0]
                    map_id = '_'.join(parts[1:-1]) if cf_type in img_path.stem else '_'.join(parts[1:])
                    
                    # Create a simple task for counterfactual
                    task_id = f"cf-{cf_type}-{country}-{map_id}"
                    task_data = {
                        "id": task_id,
                        "map_image": f"{task_id}.png",
                        "context": f"Counterfactual {cf_type} map - {country}",
                        "type": "choropleth_counterfactual",
                        "source": "mapwise",
                        "questions": [
                            {
                                "q": "What type of data pattern do you observe in this map?",
                                "a": f"This is a {cf_type} counterfactual map",
                                "type": "short_answer"
                            }
                        ],
                        "metadata": {
                            "counterfactual_type": cf_type,
                            "country": country,
                            "original_map_id": map_id
                        }
                    }
                    
                    # Save task
                    task_file = self.output_path / f"{task_id}.json"
                    with open(task_file, 'w') as f:
                        json.dump(task_data, f, indent=2)
                    
                    # Copy image
                    target_file = self.output_path / f"{task_id}.png"
                    shutil.copy2(img_path, target_file)


def main():
    parser = argparse.ArgumentParser(
        description="Integrate MapWise dataset into MapBench.Live"
    )
    
    parser.add_argument(
        "--mapwise-path",
        type=str,
        required=True,
        help="Path to the MapWise dataset directory"
    )
    
    parser.add_argument(
        "--countries",
        type=str,
        nargs="+",
        default=["usa", "india", "china"],
        help="Countries to integrate (default: all)"
    )
    
    parser.add_argument(
        "--image-variant",
        type=str,
        choices=["with_annotations", "wo_annotations", "hatched"],
        default="with_annotations",
        help="Image variant to use (default: with_annotations)"
    )
    
    parser.add_argument(
        "--include-counterfactuals",
        action="store_true",
        help="Include counterfactual examples"
    )
    
    parser.add_argument(
        "--output-path",
        type=str,
        default="data/tasks",
        help="Output directory for tasks (default: data/tasks)"
    )
    
    args = parser.parse_args()
    
    # Initialize integrator
    integrator = MapWiseIntegrator(args.mapwise_path, args.output_path)
    
    # Integrate each country
    for country in args.countries:
        print(f"\nIntegrating {country}...")
        integrator.integrate_country(country, args.image_variant)
    
    # Integrate counterfactuals if requested
    if args.include_counterfactuals:
        print("\nIntegrating counterfactuals...")
        integrator.integrate_counterfactuals()
    
    print("\nIntegration complete!")


if __name__ == "__main__":
    main()