"""
Test script to measure accuracy on full dataset
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from utils.plate_detector import PlateDetector
from utils.config import config
from utils.annotation_parser import AnnotationParser
import os
import time

detector = PlateDetector()
parser = AnnotationParser(config.ANNOTATIONS_FILE)

# Test on 30% of dataset (approx 60 images)
all_annotations = parser.get_annotations()
test_count = max(30, len(all_annotations) // 3)  # 30% or at least 30 images
annotations = all_annotations[:test_count]

correct = 0
total = 0
times = []
failed_detections = 0

print(f"\n{'='*70}")
print(f"ACCURACY TEST - {test_count} images (30% of dataset)")
print(f"{'='*70}\n")

for idx, ann in enumerate(annotations, 1):
    image_path = os.path.join(config.PHOTOS_DIR, ann.image_name)
    if not os.path.exists(image_path):
        print(f"[{idx:3d}] SKIP {ann.image_name:15} - file not found")
        continue
    
    result = detector.detect_and_recognize(image_path)
    total += 1
    
    detected = result.plate_text.upper() if result.plate_text else ''
    ground_truth = ann.plate_number.upper()
    
    if not detected:
        failed_detections += 1
        status = "FAIL (no detection)"
    else:
        match = detected == ground_truth
        if match:
            correct += 1
        status = "PASS" if match else "FAIL"
    
    times.append(result.processing_time)
    
    # Print progress every 10 images
    if idx % 10 == 0 or idx == 1:
        print(f"[{idx:3d}] {ann.image_name:15} | GT: {ground_truth:10} | Det: {detected:10} | {status}")

print(f"\n{'='*70}")
print(f"RESULTS:")
print(f"  Total images tested: {total}")
print(f"  Correct detections: {correct}/{total} = {100*correct/total:.1f}%")
print(f"  Failed detections: {failed_detections}")
print(f"  Total processing time: {sum(times):.2f}s")
print(f"  Avg time per image: {sum(times)/len(times):.3f}s")
print(f"  Time for 100 images: {(sum(times)/len(times)) * 100:.1f}s")
print(f"{'='*70}\n")

# Check grading criteria
accuracy_pct = 100 * correct / total if total > 0 else 0
time_100 = (sum(times)/len(times)) * 100 if times else 999

print(f"GRADING CRITERIA:")
print(f"  Accuracy >= 60%: {accuracy_pct:.1f}% {'PASS' if accuracy_pct >= 60 else 'FAIL'}")
print(f"  Time <= 60s for 100 images: {time_100:.1f}s {'PASS' if time_100 <= 60 else 'FAIL'}")
