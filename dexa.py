import streamlit as st
from datetime import datetime, date
import io
import requests
import json
import mysql.connector
import hashlib
import uuid
from supabase import create_client
import base64
import weasyprint
from jinja2 import Template
from PIL import Image as PILImage, ImageDraw, ImageFont
import time
import tempfile
import os
from pathlib import Path
import re

# =============================================================================
# WEAZYPRINT PDF GENERATOR FOR EXACT HTML REPLICATION
# =============================================================================
class WeasyPrintPDFGenerator:
    def __init__(self):
         # Create a static directory structure for images (from second code)
        self.static_dir = Path("static")
        self.images_dir = self.static_dir / "images"
        
        # Create directories if they don't exist
        self.images_dir.mkdir(parents=True, exist_ok=True)
        
        # Store your static images in these paths
        self.static_images = {
            'vital_insights_logo': self.images_dir / "vital_insights_logo.png",
            'fingerprint_icon': self.images_dir / "fingerprint_icon.png",
            'body_outline': self.images_dir / "body_outline.png",
            'ap_spine_placeholder': self.images_dir / "ap_spine_placeholder.png",
            'femur_placeholder': self.images_dir / "femur_placeholder.png",
            'fat_distribution_placeholder': self.images_dir / "fat_distribution_placeholder.png",
        }
        
        # Create placeholder images if they don't exist
        self._setup_static_images()
        self.html_template = Template("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DEXA Body Composition Report</title>
    <link href="https://fonts.googleapis.com/css2?family=Blinker:wght@300;400;600;700;800;900&display=swap" rel="stylesheet">
    <style>
        * { 
            font-family: 'Blinker', sans-serif; 
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body { background: white; margin: 0; padding: 0; }
        
        .page {
            width: 210mm;
            height: 297mm;
            padding: 10mm 15mm;
            box-sizing: border-box;
            page-break-after: always;
            background: white;
            position: relative;
        }
        
        .page:last-child { page-break-after: auto; }
        
        @page { size: A4; margin: 0; }
        
        @media print {
            body { margin: 0; padding: 0; }
            .page { margin: 0; box-shadow: none; }
        }
        
        /* Navigation Header */
        .nav-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-top: 2.5px solid #FF6B3D;
            padding-bottom: 6px;
            margin-top:20px;
            margin-bottom: 10px;
        }
        
        .nav-tabs {
            display: flex;
            gap: 115px;
            font-size: 10px; /* Increased from 8px */
            font-weight: 700;
            letter-spacing: 0.3px;
        }
        
        .nav-tab {
            color: #999;
            text-transform: uppercase;
        }
        
        .nav-tab.active { color: #FF6B3D; }
        
        .patient-header {
            text-align: center;
        }
        
        .patient-name {
            font-size: 14px; /* Increased from 12px */
            font-weight: 700;
            color: #FF6B3D;
        }
        
        .patient-meta {
            font-size: 9px; /* Increased from 7px */
            color: #666;
            margin-top: 2px;
        }
        
        /* Cover Page */
        .cover-content {
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            height: 100%;
            position: relative;
        }
        
        .cover-logo-top {
            position: absolute;
            top: 70px;
            left: 50%;
            transform: translateX(-50%);
            width: 220px; /* Increased from 160px */
            height:220px;
        }
        
        .cover-patient {
            font-size: 44px; /* Increased from 40px */
            font-weight: 700;
            color: #FF6B3D;
            padding-bottom: 10px;
            border-bottom: 2px solid #ccc;
            min-width: 260px;
            text-align: center;
        }
        
        .cover-logo-bottom {
            position: absolute;
            bottom: 40px;
            left: 50%;
            transform: translateX(-50%);
            text-align: center;
        }
        
        .cover-logo-bottom img {
            width: 60px; /* Increased from 50px */
            height: 60px; /* Increased from 50px */
            margin-bottom: 6px;
        }
        
        .cover-footer-text {
            font-size: 18px; /* Increased from 12px */
            color: #FF6B3D;
            font-weight: 600;
        }
        
        /* Headers */
        .section-title {
            font-size: 13px; /* Increased from 11px */
            font-weight: 700;
            color: #333;
            margin: 8px 0 6px 0;
            text-transform: uppercase;
            letter-spacing: 0.4px;
        }
        
        .subsection-title {
            font-size: 11px; /* Increased from 9px */
            font-weight: 700;
            color: #555;
            margin: 6px 0 4px 0;
        }
        
        /* Metric Boxes */
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 6px;
            margin: 8px 0;
        }
        
        .metric-box {
            border: 2px solid;
            border-radius: 5px;
            padding: 10px 8px; /* Increased padding */
            text-align: center;
        }
        
        .metric-label {
            font-size: 9px; /* Increased from 7px */
            font-weight: 700;
            color: #888;
            text-transform: uppercase;
            margin-bottom: 4px;
        }
        
        .metric-value {
            font-size: 22px; /* Increased from 18px */
            font-weight: 700;
            line-height: 1;
        }
        
        .metric-unit {
            font-size: 10px; /* Increased from 8px */
            color: #666;
            margin-top: 2px;
        }
        
        /* Status Boxes */
        .status-box {
            border-left: 3px solid;
            padding: 10px 12px; /* Increased padding */
            border-radius: 3px;
            margin: 6px 0;
        }
        
        .box-red {
            background: #FFE5E0;
            border-left-color: #FF6B3D;
        }
        
        .box-green {
            background: #E8F5E9;
            border-left-color: #4CAF50;
        }
        
        .box-yellow {
            background: #FFF8E1;
            border-left-color: #FFA500;
        }
        
        .box-title {
            font-size: 10px; /* Increased from 8px */
            font-weight: 700;
            text-transform: uppercase;
            margin-bottom: 3px;
        }
        
        .box-content {
            font-size: 10px; /* Increased from 8px */
            line-height: 1.4;
        }
        
        /* Risk Scale */
        .risk-scale {
            display: flex;
            height: 32px; /* Increased from 28px */
            margin: 8px 0;
            border-radius: 3px;
            overflow: hidden;
        }
        
        .scale-segment {
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 700;
            font-size: 9px; /* Increased from 7.5px */
            text-align: center;
            line-height: 1.1;
        }
        
        .scale-green { background: #4CAF50; }
        .scale-yellow { background: #FFA500; }
        .scale-red { background: #FF6B3D; }
        
        /* Tables */
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 6px 0;
            font-size: 9px; /* Increased from 7.5px */
        }
        
        thead {
            background: #FF6B3D;
            color: white;
        }
        
        th, td {
            padding: 6px 8px; /* Increased padding */
            text-align: left;
            border-bottom: 1px solid #eee;
        }
        
        th {
            font-weight: 700;
            text-transform: uppercase;
            font-size: 9px; /* Increased from 7px */
        }
        
        tbody tr:nth-child(even) {
            background: #f9f9f9;
        }
        
        /* Grid Layouts */
        .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
        .grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; }
        .grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 6px; }
        
        /* Text Styles */
        .text-center { text-align: center; }
        .text-sm { font-size: 10px; } /* Increased from 8px */
        .text-xs { font-size: 9px; } /* Increased from 7px */
        .font-bold { font-weight: 700; }
        .text-gray { color: #666; }
        .text-orange { color: #FF6B3D; }
        
        /* Images */
        .image-box {
            border: 1px solid #eee;
            border-radius: 3px;
            padding: 8px; /* Increased padding */
            text-align: center;
            background: #f9f9f9;
        }
        
        .image-box img {
            width: 100%;
            height: auto;
            max-height: 140px; /* Increased from 130px */
            object-fit: contain;
        }
        
        /* Donut Charts - SIMPLIFIED VERSION */
       
        
        .assymetry-main-row {
            display: flex;
            width: 100%;
            justify-content: space-between;
            align-items: flex-start;
            gap: 20px;
        }
        
        .assymetry-col {
            display: flex;
            flex-direction: column;
            gap: 18px;
            flex: 1;
        }
        
        .assymetry-image-center {
            display: flex;
            flex-direction: column;
            align-items: center;
            min-width: 180px; /* Increased from 160px */
            max-width: 220px; /* Increased from 200px */
            margin: 0 10px;
        }
        
        .assymetry-image-center .asy-label {
            font-size: 15px; /* Increased from 13px */
            font-weight: bold;
            color: #ff6b3d;
            margin-bottom: 6px;
            text-align: center;
        }
        
        .assymetry-image-center .asy-label.green {
            color: #4CAF50;
            margin-top: 8px;
        }

    /* SVG Donut Charts - WeasyPrint Compatible */
.donut-chart-svg {
    width: 60px;
    height: 60px;
    transform: rotate(-90deg); /* Start from top */
}

.donut-wrapper {
    display: inline-block;
    position: relative;
    text-align: center;
}

.donut-label {
    font-size: 8px;
    font-weight: 700;
    color: #666;
    margin-top: 2px;
}      
.donut-chart-svg circle {
  stroke-width: 6;
}
        /* Additional size increases for specific elements */
        .body-zone {
            font-size: 16px; /* Increased from 14px */
            font-weight: 700;
            color: #333;
            margin: 4px 0;
        }
        
        .recommendation-list {
            font-size: 9px; /* Increased from 7.5px */
            line-height: 1.5;
        }
        
        .risk-profile-title {
            font-size: 16px; /* Increased from 14px */
            font-weight: 700;
        }
        
        .risk-box-value {
            font-size: 24px; /* Increased from 20px */
            font-weight: 700;
            margin-top: 30px;
            margin-bottom:30px;
        }
        
        .asymmetry-percentage {
            font-size: 18px; /* Increased from 16px */
            font-weight: 700;
        }
        
        /* Simplified donut chart alternative */
        .composition-breakdown {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 4px;
        }
        
        .composition-item {
            display: flex;
            align-items: center;
            gap: 5px;
            font-size: 9px;
        }
        
        .color-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
        }
        
        .color-bone { background: #999; }
        .color-muscle { background: #4CAF50; }
        .color-fat { background: #FF6B3D; }
        .body-fat-description {
     /* center text */
    margin-top:12px;     /* space above description */
}
.visceral_fat_description{
  margin-top:12px;
}
    </style>
</head>
<body>
    <!-- PAGE 1: COVER -->
    <div class="page">
        <div class="cover-content">
            <img src="images/vital_insights_logo.png" alt="Vital Insights" class="cover-logo-top">
            <div class="cover-patient">{{ patient_name }}</div>
            <div class="cover-logo-bottom">
                <img src="images/fingerprint_icon.png" alt="Icon">
                <div class="cover-footer-text">Vital Dexa</div>
            </div>
        </div>
    </div>

    <!-- PAGE 2: SUMMARY -->
    <div class="page">
        <div class="patient-header" style="text-align: center;">
            <div class="patient-name">{{ patient_name }}, {{ age }}/{{ gender }}</div>
            <div class="patient-meta">Patient ID: {{ patient_id }} | Report ID: {{ report_id }} | Date: {{ report_date }}</div>
        </div>
        
        <div class="nav-header">
            <div class="nav-tabs">
                <span class="nav-tab active">SUMMARY</span>
                <span class="nav-tab">BONE HEALTH</span>
                <span class="nav-tab">FAT DISTRIBUTION</span>
                <span class="nav-tab">ASYMMETRY</span>
                <span class="nav-tab">TOTAL RISK</span>
            </div>
        </div>

        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <h3 class="section-title" style="margin: 0;">YOUR BODY COMPOSITION</h3>
            <div class="text-xs text-gray font-bold">HEIGHT: {{ height }} CM | WEIGHT: {{ total_mass }} KGS</div>
        </div>

        <!-- Main Metrics Row -->
        <div class="metrics-grid">
            <div class="metric-box" style="background:white; border-color: #FF6B3D;">
                <div class="metric-label text-orange">FAT MASS</div>
                <div class="metric-value">{{ fat_mass }}kg +</div>
            </div>
            <div class="metric-box" style="background: white; border-color: #4CAF50;">
                <div class="metric-label" style="color: #4CAF50;">LEAN MASS</div>
                <div class="metric-value" style="color: #4CAF50;">{{ lean_mass }}kg +</div>
            </div>
            <div class="metric-box" style="background: white; border-color: #2196F3;">
                <div class="metric-label" style="color: #2196F3;">BONE MASS</div>
                <div class="metric-value" style="color: #2196F3;">{{ bone_mass }}kg =</div>
            </div>
            <div class="metric-box" style="border-color: #999;">
                <div class="metric-label">TOTAL MASS</div>
                <div class="metric-value">{{ total_mass }}kg</div>
            </div>
        </div>

        <!-- Smaller Data Highlights -->
        <div class="metrics-grid" style="margin: 8px 0;">
            <div class="metric-box" style="background:#FFE5E0; border-color:#FFB3A6;">
                <div class="metric-label">BODY FAT<br>(PERCENTAGE)</div>
                <div style="font-size: 24px; font-weight: 700; color: #FF6B3D; margin: 3px 0; line-height: 1;">{{ body_fat_percentage }} %</div>
            </div>
            <div class="metric-box" style="background: #E8F5E9; border-color: #A5D6A7;">
                <div class="metric-label" style="color: #4CAF50;">MUSCLE MASS<br>(ALMI)</div>
                <div style="font-size: 20px; font-weight: 700; color: #4CAF50; margin: 3px 0; line-height: 1;">{{ muscle_mass_almi }} kg/m²</div>
            </div>
            <div class="metric-box" style="background: #E3F2FD; border-color: #90CAF9;">
                <div class="metric-label" style="color: #2196F3;">BONE DENSITY<br>(T-SCORE)</div>
                <div style="font-size: 24px; font-weight: 700; color: #2196F3; margin: 3px 0; line-height: 1;">{{ bone_density_t_score }}</div>
            </div>
            <div style="display: flex; flex-direction: column; justify-content: center; gap: 5px; padding-left: 8px;">
                <div style="display: flex; align-items: center; gap: 5px;">
                    <div style="width: 10px; height: 10px; border-radius: 50%; background: #4CAF50;"></div>
                    <span class="text-xs font-bold">In Range</span>
                </div>
                <div style="display: flex; align-items: center; gap: 5px;">
                    <div style="width: 10px; height: 10px; border-radius: 50%; background: #FFA500;"></div>
                    <span class="text-xs font-bold">Suboptimal</span>
                </div>
                <div style="display: flex; align-items: center; gap: 5px;">
                    <div style="width: 10px; height: 10px; border-radius: 50%; background: #FF6B3D;"></div>
                    <span class="text-xs font-bold">Needs Attention</span>
                </div>
            </div>
        </div>

        <!-- "See page X for more" notes below each box -->
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 6px; margin-bottom: 8px;">
            <div class="text-xs text-gray" style="text-align: center; margin-top: 3px;">See page 3 for more</div>
            <div class="text-xs text-gray" style="text-align: center; margin-top: 3px;">See page 4 for more</div>
            <div class="text-xs text-gray" style="text-align: center; margin-top: 3px;">See page 2 for more</div>
            <div></div>
        </div>
        
        <div style="margin-top: 10px;">
            <div class="box-title" style="font-size: 11px; color: #333;">YOU ARE IN THE...</div>
        </div>
        <div style="margin-top: 10px; padding: 12px; background: #FFF8E1; border-left: 3px solid #FFA500; border-radius: 4px;">
            
            <div class="body-zone" style="text-align:center;">{{ body_zone }}</div>
            <div class="text-sm" style="text-align:center;color: #666; font-style: italic;">{{ zone_description }}</div>
        </div>

        <div style="margin-top: 10px;">
            <div class="box-title" style="font-size: 11px; color: #333;">YOU ARE...</div>
        </div>

        <div class="grid-2" style="margin-top: 6px;">
            <div class="status-box box-green">
                <div class="box-title" style="text-align:center;color: #4CAF50;">{{ muscle_assessment_title }}</div>
                <div class="box-content">{{ muscle_assessment_description }}</div>
            </div>
            <div class="status-box box-red">
                <div class="box-title text-orange"style="text-align:center;">{{ fat_assessment_title }}</div>
                <div class="box-content">{{ fat_assessment_description }}</div>
            </div>
        </div>

        <h3 class="section-title" style="margin-top: 10px;">AND THESE ARE OUR SUGGESTIONS...</h3>
        <div class="grid-2">
            <div>
                <div class="subsection-title text-orange">🔧 NUTRITION</div>
                <ul class="recommendation-list" style="margin: 0; padding-left: 14px;">
                    {% for rec in nutrition_recommendations %}
                    <li>{{ rec }}</li>
                    {% endfor %}
                </ul>
            </div>
            <div>
                <div class="subsection-title text-orange">🏋️ TRAINING</div>
                <ul class="recommendation-list" style="margin: 0; padding-left: 14px;">
                    {% for rec in training_recommendations %}
                    <li>{{ rec }}</li>
                    {% endfor %}
                </ul>
            </div>
        </div>
    </div>

    <!-- PAGE 3: BONE HEALTH -->
    <div class="page">
        <div class="patient-header" style="text-align: center;">
            <div class="patient-name">{{ patient_name }}, {{ age }}/{{ gender }}</div>
            <div class="patient-meta">Patient ID: {{ patient_id }} | Report ID: {{ report_id }} | Date: {{ report_date }}</div>
        </div>
        
        <div class="nav-header">
            <div class="nav-tabs">
                <span class="nav-tab">SUMMARY</span>
                <span class="nav-tab active">BONE HEALTH</span>
                <span class="nav-tab">FAT DISTRIBUTION</span>
                <span class="nav-tab">ASYMMETRY</span>
                <span class="nav-tab">TOTAL RISK</span>
            </div>
        </div>

        <div class="status-box {{ bone_health_box_class }}" style="margin: 12px 0; border-left-width: 0; text-align: center;">
            <div class="box-title" style="color: {{ bone_health_box_color }};">{{ bone_health_title }}</div>
            
        </div>
        <div class="bone_health_description">{{ bone_health_description }}</div>
        <div style="text-align: center; margin: 8px 0 4px 0;">
            <div class="text-xs font-bold text-orange" style="text-transform: uppercase;">YOU ARE HERE</div>
            <div style="font-size: 20px; font-weight: 700; color: #333;">▼</div>
        </div>

        <div class="risk-scale">
            <div class="scale-segment scale-green" style="width: 45.71%;">NORMAL<br>LOW FRACTURE RISK</div>
            <div class="scale-segment scale-yellow" style="width: 31.43%;">OSTEOPENIA<br>MILD FRACTURE RISK</div>
            <div class="scale-segment scale-red" style="width: 22.86%;">OSTEOPOROSIS<br>HIGH FRACTURE RISK</div>
        </div>

        <div style="display: flex; justify-content: space-between; font-size: 10px; font-weight: 700; color: #666; margin-top: 3px; margin-bottom: 10px;">
            <span>1.0</span>
            <span style="margin-left: -15px;">{{ bone_density_t_score }}</span>
            <span style="margin-left: -10px;">-1.0</span>
            <span style="margin-right: -8px;">-2.5</span>
        </div>

        <div class="grid-2" style="margin: 10px 0;">
            <div>
                <div class="subsection-title">T-score</div>
                <div class="text-sm">This compares your bone density to that of a healthy young adult (around age 30). It's the main number doctors use to assess your bone strength.</div>
                <div class="subsection-title" style="margin-top: 10px;">Z-score</div>
                <div class="text-sm">This compares your bone density to other people of the same age, sex, and body size. It helps us understand if your bone health is typical for someone like you.</div>
            </div>
            <div>
                <div class="subsection-title">Osteopenia</div>
                <div class="text-sm">This is your early warning zone. A T-score between -1.0 and -2.5 means your bones are starting to weaken. It's not a diagnosis, but it's a chance to take action before things get worse.</div>
                <div class="subsection-title" style="margin-top: 10px;">Osteoporosis</div>
                <div class="text-sm">A T-score below -2.5 means your bones are fragile and more prone to fractures. This needs attention, talk to a doctor about ways to strengthen and protect your bones.</div>
            </div>
        </div>

        <!-- AP-SPINE SECTION -->
        <div class="grid-2" style="margin-top: 10px; grid-template-columns: 120px 1fr; align-items: flex-start;">
            <div>
                <div class="subsection-title">AP-SPINE</div>
                <div class="image-box" style="padding: 6px;">
                    <img src="images/ap_spine_placeholder.png" alt="AP-Spine" style="width:90px; max-width:90px; max-height:130px; margin:0 auto;">
                </div>
            </div>
            <div>
                <table>
                    <thead>
                        <tr>
                            <th>REGION</th>
                            <th>BMD(G/CM²)</th>
                            <th>T SCORE</th>
                            <th>Z SCORE</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for m in ap_spine_measurements %}
                        <tr>
                            <td>{{ m.region }}</td>
                            <td>{{ m.bmd }}</td>
                            <td>{{ m.t_score }}</td>
                            <td>{{ m.z_score }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>

        <!-- RIGHT FEMUR SECTION -->
        <div class="grid-2" style="margin-top: 10px; grid-template-columns: 120px 1fr; align-items: flex-start;">
            <div>
                <div class="subsection-title">RIGHT FEMUR</div>
                <div class="image-box" style="padding: 6px;">
                    <img src="images/right_femur.png" alt="Right Femur" style="width:90px; max-width:90px; max-height:130px; margin:0 auto;">
                </div>
            </div>
            <div>
                <table>
                    <thead>
                        <tr>
                            <th>REGION</th>
                            <th>BMD(G/CM²)</th>
                            <th>T SCORE</th>
                            <th>Z SCORE</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for m in right_femur_measurements %}
                        <tr>
                            <td>{{ m.region }}</td>
                            <td>{{ m.bmd }}</td>
                            <td>{{ m.t_score }}</td>
                            <td>{{ m.z_score }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>

        <!-- LEFT FEMUR SECTION -->
        <div class="grid-2" style="margin-top: 10px; grid-template-columns: 120px 1fr; align-items: flex-start;">
            <div>
                <div class="subsection-title">LEFT FEMUR</div>
                <div class="image-box" style="padding: 6px;">
                    <img src="images/left_femur.png" alt="Left Femur" style="width:90px; max-width:90px; max-height:130px; margin:0 auto;">
                </div>
            </div>
            <div>
                <table>
                    <thead>
                        <tr>
                            <th>REGION</th>
                            <th>BMD(G/CM²)</th>
                            <th>T SCORE</th>
                            <th>Z SCORE</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for m in left_femur_measurements %}
                        <tr>
                            <td>{{ m.region }}</td>
                            <td>{{ m.bmd }}</td>
                            <td>{{ m.t_score }}</td>
                            <td>{{ m.z_score }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <!-- PAGE 4: FAT DISTRIBUTION -->
    <div class="page">
        <div class="patient-header">
            <div class="patient-name">{{ patient_name }}, {{ age }}/{{ gender }}</div>
            <div class="patient-meta">Patient ID: {{ patient_id }} | Report ID: {{ report_id }} | Date: {{ report_date }}</div>
        </div>
        
        <div class="nav-header">
            <div class="nav-tabs">
                <span class="nav-tab">SUMMARY</span>
                <span class="nav-tab">BONE HEALTH</span>
                <span class="nav-tab active">FAT DISTRIBUTION</span>
                <span class="nav-tab">ASYMMETRY</span>
                <span class="nav-tab">TOTAL RISK</span>
            </div>
        </div>

        <div class="status-box {{ body_fat_box_class }}">
            <div class="box-title"style="text-align:center;">{{ body_fat_title }}</div>
        </div>
        <div class="body-fat-description">
    {{ body_fat_description }}
</div>
        <div style="text-align: center; margin: 4px 0;">
            <div class="text-xs font-bold text-orange" style="text-transform: uppercase;">YOU ARE HERE</div>
            <div style="font-size: 20px; font-weight: 700; color: #333;">▼</div>
        </div>

        <div class="risk-scale" style="height: 28px;">
            <div class="scale-segment scale-red" style="width: 25%;">UNDER</div>
            <div class="scale-segment scale-green" style="width: 40%;">IN RANGE</div>
            <div class="scale-segment scale-red" style="width: 35%;">OVER</div>
        </div>

        <div style="display: flex; justify-content: space-between; font-size: 10px; font-weight: 700; color: #666; margin-top: 2px; margin-bottom: 12px;">
            <span style="margin-left: 20%;">11.2 %</span>
            <span style="margin-right: 15%;">30.2 %</span>
            <span style="margin-right: -8px;">{{ body_fat_percentage }} %</span>
        </div>

        <div class="status-box {{ visceral_fat_box_class }}" style="margin-top: 15px;">
            <div class="box-title">{{ visceral_fat_title }}</div>
            
        </div>
        <div class="visceral_fat_description">{{ visceral_fat_description }}</div>
        <div style="text-align: center; margin: 4px 0;">
            <div class="text-xs font-bold text-orange" style="text-transform: uppercase;">YOU ARE HERE</div>
            <div style="font-size: 20px; font-weight: 700; color: #333;">▼</div>
        </div>

        <div class="risk-scale" style="height: 28px;">
            <div class="scale-segment scale-green" style="width: 50%;">IN RANGE</div>
            <div class="scale-segment scale-red" style="width: 50%;">OVER</div>
        </div>

        <div style="display: flex; justify-content: space-between; font-size: 10px; font-weight: 700; color: #666; margin-top: 2px; margin-bottom: 15px;">
            <span style="margin-left: 45%;">100 cm²</span>
            <span style="margin-right: -8px;">{{ visceral_fat_area }} cm²</span>
        </div>

        <div style="display: flex; align-items: center; margin-top: 24px;">
            <!-- Image: narrow column -->
            <div style="width: 130px; min-width: 110px;">
                <div class="image-box" style="background: white; border-color: #ddd; padding: 10px;">
                    <img src="images/fat_distribution_placeholder.png" alt="Fat Distribution" style="width:80px; max-width:90px; height:auto; display:block; margin:0 auto;">
                </div>
            </div>
            <!-- Box + ratio text: wider column -->
            <div style="flex: 1; margin-left: 24px; display: flex; flex-direction: column; justify-content: center;">
                <div class="status-box {{ ag_ratio_box_class }}" style="margin-bottom: 0; text-align: center;">
                    <div class="box-title" style="color: {{ ag_ratio_box_color }};">{{ ag_ratio_title }}</div>
                </div>
                <div style="font-size: 10px; color: #444; margin-top: 12px;">
                    {{ ag_ratio_description }}
                </div>
            </div>
        </div>
    </div>
<!-- PAGE 5: ASYMMETRY -->
<div class="page" id="page-5">
    <div class="patient-header">
        <div class="patient-name">{{ patient_name }}, {{ age }}/{{ gender }}</div>
        <div class="patient-meta">Patient ID: {{ patient_id }} | Report: {{ report_id }} | {{ report_date }}</div>
    </div>
    
    <div class="nav-header">
        <div class="nav-tabs">
            <span class="nav-tab">SUMMARY</span>
            <span class="nav-tab">BONE HEALTH</span>
            <span class="nav-tab">FAT DISTRIBUTION</span>
            <span class="nav-tab active">ASYMMETRY</span>
            <span class="nav-tab">TOTAL RISK</span>
        </div>
    </div>

    <div class="status-box {{ asymmetry_box_class }}" style="border-left-width: 0; text-align: center; margin: 8px 0;">
        <div class="box-title" style="color: {{ asymmetry_box_color }};">{{ asymmetry_title }}</div>
        
    </div>
    <div class="asymmetry_description">{{ asymmetry_description }}</div>
    <!-- Above symmetry row: FFMI, Trunk, ALMI -->
    <div style="display: flex; justify-content: center; gap: 18px; margin-bottom: 24px;">
        <div class="metric-box" style="border-color: #FF6B3D; width: 240px;">
            <div style="font-size:30px;margin-bottom:20px;">{{ ffmi }} kg/m²</div>
            <div style="font-size:22px;text-align:left;">FFMI</div>
            <div style="font-size:18px;text-align:left">(FAT FREE MASS INDEX)</div>
        </div>
        <div class="metric-box" style="border-color:#FF6B3D; width: 240px;">
          <div style="font-size:13px; color:#FF6B3D;">TRUNK TOTAL: {{ trunk_total }}KG</div>
            <div class="donut-wrapper">
                <!-- SVG Donut Chart for Trunk -->
                <svg class="donut-chart-svg" width="60" height="60" viewBox="0 0 42 42">
                    <circle cx="21" cy="21" r="15.915" fill="transparent" stroke="#f0f0f0" stroke-width="3"/>
                    <!-- Bone segment -->
                    <circle cx="21" cy="21" r="15.915" fill="transparent" stroke="#999" stroke-width="3"
                            stroke-dasharray="{{ trunk_bone_percent }} {{ 100 - trunk_bone_percent }}"
                            stroke-dashoffset="25"/>
                    <!-- Muscle segment -->
                    <circle cx="21" cy="21" r="15.915" fill="transparent" stroke="#4CAF50" stroke-width="3"
                            stroke-dasharray="{{ trunk_muscle_percent }} {{ 100 - trunk_muscle_percent }}"
                            stroke-dashoffset="{{ 25 - trunk_bone_percent }}"/>
                    <!-- Fat segment -->
                    <circle cx="21" cy="21" r="15.915" fill="transparent" stroke="#FF6B3D" stroke-width="3"
                            stroke-dasharray="{{ trunk_fat_percent }} {{ 100 - trunk_fat_percent }}"
                            stroke-dashoffset="{{ 25 - trunk_bone_percent - trunk_muscle_percent }}"/>
                </svg>
            </div>
            
            <div style="font-size:12px;">Bone: {{ trunk_bone_percent }}% | Muscle: {{ trunk_muscle_percent }}% | Fat: {{ trunk_fat_percent }}%</div>
        </div>
        <div class="metric-box" style="border-color: #FF6B3D; width: 240px;">
            <div style="font-size:30px;margin-bottom:20px">{{ muscle_mass_almi }} kg/m²</div>
            <div style="font-size:22px;text-align:left">ALMI</div>
            <div style="font-size:18px;text-align:left">(APPENDICULAR LEAN MASS INDEX)</div>
        </div>
    </div>

    <!-- Main flex row for symmetry content -->
    <div style="display: flex; justify-content: space-between; gap: 26px;">
        <!-- Left side: Right Arm & Right Leg -->
        <div style="flex: 1; display: flex; flex-direction: column; gap: 20px;">
            <!-- Right Arm -->
            <div class="metric-box" style="border-color: #FF6B3D;">
                <div style="font-size:13px; color:#FF6B3D; font-weight:700; margin-bottom:6px;">TOTAL RIGHT ARM: {{ right_arm_total }}KG</div>
                <div style="display:flex; justify-content:center; gap:12px; margin-bottom:4px;">
                    <div style="display:flex; flex-direction:column; align-items:center;">
                        <div class="donut-label" style="color: #999; font-size:11px; font-weight:700; margin-bottom:2px;">BONE</div>
                        <!-- Bone Donut -->
                        <svg class="donut-chart-svg" width="60" height="60" viewBox="0 0 42 42">
                            <circle cx="21" cy="21" r="15.915" fill="transparent" stroke="#f0f0f0" stroke-width="3"/>
                            <circle cx="21" cy="21" r="15.915" fill="transparent" stroke="#999" stroke-width="3"
                                    stroke-dasharray="{{ right_arm_bone_percent }} {{ 100 - right_arm_bone_percent }}"
                                    stroke-dashoffset="25"/>
                        </svg>
                        <div style="font-size:11px; font-weight:700; margin-top:2px;">{{ right_arm_bone_percent }}%</div>
                    </div>
                    <div style="display:flex; flex-direction:column; align-items:center;">
                        <div class="donut-label" style="color: #4CAF50; font-size:11px; font-weight:700; margin-bottom:2px;">MUSCLE</div>
                        <!-- Muscle Donut -->
                        <svg class="donut-chart-svg" width="60" height="60" viewBox="0 0 42 42">
                            <circle cx="21" cy="21" r="15.915" fill="transparent" stroke="#f0f0f0" stroke-width="3"/>
                            <circle cx="21" cy="21" r="15.915" fill="transparent" stroke="#4CAF50" stroke-width="3"
                                    stroke-dasharray="{{ right_arm_muscle_percent }} {{ 100 - right_arm_muscle_percent }}"
                                    stroke-dashoffset="25"/>
                        </svg>
                        <div style="font-size:11px; font-weight:700; margin-top:2px;">{{ right_arm_muscle_percent }}%</div>
                    </div>
                    <div style="display:flex; flex-direction:column; align-items:center;">
                        <div class="donut-label" style="color: #FF6B3D; font-size:11px; font-weight:700; margin-bottom:2px;">FAT</div>
                        <!-- Fat Donut -->
                        <svg class="donut-chart-svg" width="60" height="60" viewBox="0 0 42 42">
                            <circle cx="21" cy="21" r="15.915" fill="transparent" stroke="#f0f0f0" stroke-width="3"/>
                            <circle cx="21" cy="21" r="15.915" fill="transparent" stroke="#FF6B3D" stroke-width="3"
                                    stroke-dasharray="{{ right_arm_fat_percent }} {{ 100 - right_arm_fat_percent }}"
                                    stroke-dashoffset="25"/>
                        </svg>
                        <div style="font-size:11px; font-weight:700; margin-top:2px;">{{ right_arm_fat_percent }}%</div>
                    </div>
                </div>
                <table style="width:100%; margin: 4px 0;">
                    <thead>
                        <tr>
                            <th>Region</th>
                            <th>Right Arm</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Fat (g)</td>
                            <td>{{ right_arm_fat_g }}</td>
                        </tr>
                        <tr>
                            <td>Lean (g)</td>
                            <td>{{ right_arm_lean_g }}</td>
                        </tr>
                        <tr>
                            <td>BMC (g)</td>
                            <td>{{ right_arm_bmc_g }}</td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <!-- Right Leg -->
            <div class="metric-box" style="border-color: #4CAF50;">
                <div style="font-size:13px; color:#4CAF50; font-weight:700; margin-bottom:6px;">TOTAL RIGHT LEG: {{ right_leg_total }}KG</div>
                <div style="display:flex; justify-content:center; gap:12px; margin-bottom:4px;">
                    <div style="display:flex; flex-direction:column; align-items:center;">
                        <div class="donut-label" style="color: #999; font-size:11px; font-weight:700; margin-bottom:2px;">BONE</div>
                        <!-- Bone Donut -->
                        <svg class="donut-chart-svg" width="60" height="60" viewBox="0 0 42 42">
                            <circle cx="21" cy="21" r="15.915" fill="transparent" stroke="#f0f0f0" stroke-width="3"/>
                            <circle cx="21" cy="21" r="15.915" fill="transparent" stroke="#999" stroke-width="3"
                                    stroke-dasharray="{{ right_leg_bone_percent }} {{ 100 - right_leg_bone_percent }}"
                                    stroke-dashoffset="25"/>
                        </svg>
                        <div style="font-size:11px; font-weight:700; margin-top:2px;">{{ right_leg_bone_percent }}%</div>
                    </div>
                    <div style="display:flex; flex-direction:column; align-items:center;">
                        <div class="donut-label" style="color: #4CAF50; font-size:11px; font-weight:700; margin-bottom:2px;">MUSCLE</div>
                        <!-- Muscle Donut -->
                        <svg class="donut-chart-svg" width="60" height="60" viewBox="0 0 42 42">
                            <circle cx="21" cy="21" r="15.915" fill="transparent" stroke="#f0f0f0" stroke-width="3"/>
                            <circle cx="21" cy="21" r="15.915" fill="transparent" stroke="#4CAF50" stroke-width="3"
                                    stroke-dasharray="{{ right_leg_muscle_percent }} {{ 100 - right_leg_muscle_percent }}"
                                    stroke-dashoffset="25"/>
                        </svg>
                        <div style="font-size:11px; font-weight:700; margin-top:2px;">{{ right_leg_muscle_percent }}%</div>
                    </div>
                    <div style="display:flex; flex-direction:column; align-items:center;">
                        <div class="donut-label" style="color: #FF6B3D; font-size:11px; font-weight:700; margin-bottom:2px;">FAT</div>
                        <!-- Fat Donut -->
                        <svg class="donut-chart-svg" width="60" height="60" viewBox="0 0 42 42">
                            <circle cx="21" cy="21" r="15.915" fill="transparent" stroke="#f0f0f0" stroke-width="3"/>
                            <circle cx="21" cy="21" r="15.915" fill="transparent" stroke="#FF6B3D" stroke-width="3"
                                    stroke-dasharray="{{ right_leg_fat_percent }} {{ 100 - right_leg_fat_percent }}"
                                    stroke-dashoffset="25"/>
                        </svg>
                        <div style="font-size:11px; font-weight:700; margin-top:2px;">{{ right_leg_fat_percent }}%</div>
                    </div>
                </div>
                <table style="width:100%; margin: 4px 0;">
                    <thead>
                        <tr>
                            <th>Region</th>
                            <th>Right Leg</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Fat (g)</td>
                            <td>{{ right_leg_fat_g }}</td>
                        </tr>
                        <tr>
                            <td>Lean (g)</td>
                            <td>{{ right_leg_lean_g }}</td>
                        </tr>
                        <tr>
                            <td>BMC (g)</td>
                            <td>{{ right_leg_bmc_g }}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Center: Image with symmetry % labels above and below -->
        <div style="display: flex; flex-direction: column; align-items: center; min-width: 180px; max-width:220px; margin: 0 8px;">
            <div style="font-size:15px; color:#FF6B3D; font-weight:700; text-align:center; margin-bottom:4px;">ARMS ASYMMETRY %</div>
            <div class="asymmetry-percentage" style="color:#FF6B3D;">{{ arms_asymmetry }}%</div>
            <img src="images/body_outline.png" style="width:180px; height:450px; object-fit:cover;" alt="Body Outline">
            <div style="font-size:15px; color:#4CAF50; font-weight:700; margin-top:10px; text-align:center;">LEGS ASYMMETRY %</div>
            <div class="asymmetry-percentage" style="color:#4CAF50;">{{ legs_asymmetry }}%</div>
        </div>

        <!-- Right side: Left Arm & Left Leg -->
        <div style="flex: 1; display: flex; flex-direction: column; gap: 20px;">
            <!-- Left Arm -->
            <div class="metric-box" style="border-color: #FF6B3D;">
                <div style="font-size:13px; color:#FF6B3D; font-weight:700; margin-bottom:6px;">TOTAL LEFT ARM: {{ left_arm_total }}KG</div>
                <div style="display:flex; justify-content:center; gap:12px; margin-bottom:4px;">
                    <div style="display:flex; flex-direction:column; align-items:center;">
                        <div class="donut-label" style="color: #999; font-size:11px; font-weight:700; margin-bottom:2px;">BONE</div>
                        <!-- Bone Donut -->
                        <svg class="donut-chart-svg" width="60" height="60" viewBox="0 0 42 42">
                            <circle cx="21" cy="21" r="15.915" fill="transparent" stroke="#f0f0f0" stroke-width="3"/>
                            <circle cx="21" cy="21" r="15.915" fill="transparent" stroke="#999" stroke-width="3"
                                    stroke-dasharray="{{ left_arm_bone_percent }} {{ 100 - left_arm_bone_percent }}"
                                    stroke-dashoffset="25"/>
                        </svg>
                        <div style="font-size:11px; font-weight:700; margin-top:2px;">{{ left_arm_bone_percent }}%</div>
                    </div>
                    <div style="display:flex; flex-direction:column; align-items:center;">
                        <div class="donut-label" style="color: #4CAF50; font-size:11px; font-weight:700; margin-bottom:2px;">MUSCLE</div>
                        <!-- Muscle Donut -->
                        <svg class="donut-chart-svg" width="60" height="60" viewBox="0 0 42 42">
                            <circle cx="21" cy="21" r="15.915" fill="transparent" stroke="#f0f0f0" stroke-width="3"/>
                            <circle cx="21" cy="21" r="15.915" fill="transparent" stroke="#4CAF50" stroke-width="3"
                                    stroke-dasharray="{{ left_arm_muscle_percent }} {{ 100 - left_arm_muscle_percent }}"
                                    stroke-dashoffset="25"/>
                        </svg>
                        <div style="font-size:11px; font-weight:700; margin-top:2px;">{{ left_arm_muscle_percent }}%</div>
                    </div>
                    <div style="display:flex; flex-direction:column; align-items:center;">
                        <div class="donut-label" style="color: #FF6B3D; font-size:11px; font-weight:700; margin-bottom:2px;">FAT</div>
                        <!-- Fat Donut -->
                        <svg class="donut-chart-svg" width="60" height="60" viewBox="0 0 42 42">
                            <circle cx="21" cy="21" r="15.915" fill="transparent" stroke="#f0f0f0" stroke-width="3"/>
                            <circle cx="21" cy="21" r="15.915" fill="transparent" stroke="#FF6B3D" stroke-width="3"
                                    stroke-dasharray="{{ left_arm_fat_percent }} {{ 100 - left_arm_fat_percent }}"
                                    stroke-dashoffset="25"/>
                        </svg>
                        <div style="font-size:11px; font-weight:700; margin-top:2px;">{{ left_arm_fat_percent }}%</div>
                    </div>
                </div>
                <table style="width:100%; margin: 4px 0;">
                    <thead>
                        <tr>
                            <th>Region</th>
                            <th>Left Arm</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Fat (g)</td>
                            <td>{{ left_arm_fat_g }}</td>
                        </tr>
                        <tr>
                            <td>Lean (g)</td>
                            <td>{{ left_arm_lean_g }}</td>
                        </tr>
                        <tr>
                            <td>BMC (g)</td>
                            <td>{{ left_arm_bmc_g }}</td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <!-- Left Leg -->
            <div class="metric-box" style="border-color: #4CAF50;">
                <div style="font-size:13px; color:#4CAF50; font-weight:700; margin-bottom:6px;">TOTAL LEFT LEG: {{ left_leg_total }}KG</div>
                <div style="display:flex; justify-content:center; gap:12px; margin-bottom:4px;">
                    <div style="display:flex; flex-direction:column; align-items:center;">
                        <div class="donut-label" style="color: #999; font-size:11px; font-weight:700; margin-bottom:2px;">BONE</div>
                        <!-- Bone Donut -->
                        <svg class="donut-chart-svg" width="60" height="60" viewBox="0 0 42 42">
                            <circle cx="21" cy="21" r="15.915" fill="transparent" stroke="#f0f0f0" stroke-width="3"/>
                            <circle cx="21" cy="21" r="15.915" fill="transparent" stroke="#999" stroke-width="3"
                                    stroke-dasharray="{{ left_leg_bone_percent }} {{ 100 - left_leg_bone_percent }}"
                                    stroke-dashoffset="25"/>
                        </svg>
                        <div style="font-size:11px; font-weight:700; margin-top:2px;">{{ left_leg_bone_percent }}%</div>
                    </div>
                    <div style="display:flex; flex-direction:column; align-items:center;">
                        <div class="donut-label" style="color: #4CAF50; font-size:11px; font-weight:700; margin-bottom:2px;">MUSCLE</div>
                        <!-- Muscle Donut -->
                        <svg class="donut-chart-svg" width="60" height="60" viewBox="0 0 42 42">
                            <circle cx="21" cy="21" r="15.915" fill="transparent" stroke="#f0f0f0" stroke-width="3"/>
                            <circle cx="21" cy="21" r="15.915" fill="transparent" stroke="#4CAF50" stroke-width="3"
                                    stroke-dasharray="{{ left_leg_muscle_percent }} {{ 100 - left_leg_muscle_percent }}"
                                    stroke-dashoffset="25"/>
                        </svg>
                        <div style="font-size:11px; font-weight:700; margin-top:2px;">{{ left_leg_muscle_percent }}%</div>
                    </div>
                    <div style="display:flex; flex-direction:column; align-items:center;">
                        <div class="donut-label" style="color: #FF6B3D; font-size:11px; font-weight:700; margin-bottom:2px;">FAT</div>
                        <!-- Fat Donut -->
                        <svg class="donut-chart-svg" width="60" height="60" viewBox="0 0 42 42">
                            <circle cx="21" cy="21" r="15.915" fill="transparent" stroke="#f0f0f0" stroke-width="3"/>
                            <circle cx="21" cy="21" r="15.915" fill="transparent" stroke="#FF6B3D" stroke-width="3"
                                    stroke-dasharray="{{ left_leg_fat_percent }} {{ 100 - left_leg_fat_percent }}"
                                    stroke-dashoffset="25"/>
                        </svg>
                        <div style="font-size:11px; font-weight:700; margin-top:2px;">{{ left_leg_fat_percent }}%</div>
                    </div>
                </div>
                <table style="width:100%; margin: 4px 0;">
                    <thead>
                        <tr>
                            <th>Region</th>
                            <th>Left Leg</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Fat (g)</td>
                            <td>{{ left_leg_fat_g }}</td>
                        </tr>
                        <tr>
                            <td>Lean (g)</td>
                            <td>{{ left_leg_lean_g }}</td>
                        </tr>
                        <tr>
                            <td>BMC (g)</td>
                            <td>{{ left_leg_bmc_g }}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</div>

    <!-- PAGE 6: TOTAL RISK -->
    <div class="page">
        <div class="patient-header">
            <div class="patient-name">{{ patient_name }}, {{ age }}/{{ gender }}</div>
            <div class="patient-meta">Patient ID: {{ patient_id }} | Report: {{ report_id }} | {{ report_date }}</div>
        </div>
        
        <div class="nav-header">
            <div class="nav-tabs">
                <span class="nav-tab">SUMMARY</span>
                <span class="nav-tab">BONE HEALTH</span>
                <span class="nav-tab">FAT DISTRIBUTION</span>
                <span class="nav-tab">ASYMMETRY</span>
                <span class="nav-tab active">TOTAL RISK</span>
            </div>
        </div>

        <div style="background: {{ risk_profile_color }}; color: white; padding: 12px; border-radius: 5px; text-align: center; margin: 10px 0; font-size: 16px; font-weight: 700;">
            {{ risk_profile_title }}
        </div>

        <div style="display: grid; grid-template-columns: repeat(3, 1fr) 168px; gap: 24px; margin: 35px 0;">
            <!-- Row 1: Body Fat Metrics + Risk Box 1 -->
            <div style="border:2px solid #FFB3A6; border-radius:8px; padding:20px; background:#fff; text-align:center;">
                <div class="metric-label" style="font-size:15px;">BODY FAT MASS</div>
                <div style="font-size:20px; font-weight:700; margin:10px 0;">{{ fat_mass }} kg</div>
            </div>
            
            <div style="border:2px solid #FFB3A6; border-radius:8px; padding:20px; background:#fff; text-align:center;">
                <div class="metric-label" style="font-size:15px;">BODY FAT %</div>
                <div style="font-size:20px; font-weight:700; margin:10px 0;">{{ body_fat_percentage }} %</div>
            </div>
            
            <div style="border:2px solid #FFB3A6; border-radius:8px; padding:20px; background:#fff; text-align:center;">
                <div class="metric-label" style="font-size:15px;">VISCERAL FAT AREA</div>
                <div style="font-size:20px; font-weight:700; margin:10px 0;">{{ visceral_fat_area }} cm²</div>
            </div>
            
            <div style="border-radius:8px; background:#FF6B3D; color:#fff; padding:20px; text-align:center;">
                <div style="font-size:13px; font-weight:700;">{{ unhealthy_fat_title }}</div>
                <div class="risk-box-value">{{ unhealthy_fat_level }}</div>
            </div>
            
            <!-- Row 2: T-Score and Z-Score + Risk Box 2 -->
            <div style="border:2px solid #90CAF9; border-radius:8px; padding:24px; background:#fff; text-align:center;">
                <div class="metric-label" style="font-size:15px;">TSCORE</div>
                <div style="font-size:22px; font-weight:700; margin:10px 0;">{{ bone_density_t_score }}</div>
            </div>
            
            <div style="border:2px solid #90CAF9; border-radius:8px; padding:24px; background:#fff; text-align:center;">
                <div class="metric-label" style="font-size:15px;">ZSCORE</div>
                <div style="font-size:22px; font-weight:700; margin:10px 0;">{{ z_score }}</div>
            </div>
            
            <div></div> <!-- Empty cell to maintain grid structure -->
            
            <div style="border-radius:8px; background:#E8F5E9; color:#4CAF50; padding:20px; text-align:center;">
                <div style="font-size:13px; font-weight:700;">FRACTURE RISK</div>
                <div class="risk-box-value">{{ fracture_risk }}</div>
            </div>
            
            <!-- Row 3: FFMI and ALMI + Risk Box 3 -->
            <div style="border:2px solid #A5D6A7; border-radius:8px; padding:24px; background:#fff; text-align:center;">
                <div class="metric-label" style="font-size:15px;">FFMI</div>
                <div style="font-size:22px; font-weight:700; margin:10px 0;">{{ ffmi }} kg/m²</div>
            </div>
            
            <div style="border:2px solid #A5D6A7; border-radius:8px; padding:24px; background:#fff; text-align:center;">
                <div class="metric-label" style="font-size:15px;">ALMI</div>
                <div style="font-size:22px; font-weight:700; margin:10px 0;">{{ muscle_mass_almi }} kg/m²</div>
            </div>
            
            <div></div> <!-- Empty cell to maintain grid structure -->
            
            <div style="border-radius:8px; background:#E8F5E9; color:#388E3C; padding:20px; text-align:center;">
                <div style="font-size:13px; font-weight:700;">MUSCLE LOSS RISK</div>
                <div class="risk-box-value">{{ muscle_loss_risk }}</div>
            </div>
        </div>
        
        <div style="position: absolute; bottom: 50px; left: 50%; transform: translateX(-50%); text-align: center;">
            <img src="images/fingerprint_icon.png" alt="Fingerprint Icon" style="width: 50px; height: 50px;">
        </div>
    </div>
</body>
</html>""")
        
        # Initialize Supabase storage
        self.supabase_storage = SupabaseStorageManager()
         # Set base URL for images - FIXED
        self._setup_base_urls()
    def _setup_base_urls(self):
        """Setup proper base URLs for images - FIXED VERSION"""
        try:
            # For WeasyPrint, we need absolute file paths with file:// protocol
            self.base_image_urls = {}
            image_mappings = {
            'vital_insights_logo': 'vital_insights_logo_url',
            'fingerprint_icon': 'fingerprint_icon_url', 
            'body_outline': 'body_outline_image_url',  # This was the missing key!
            'ap_spine_placeholder': 'ap_spine_placeholder_url',
            'femur_placeholder': 'femur_placeholder_url',
            'fat_distribution_placeholder': 'fat_distribution_placeholder_url'
        }
            for key, image_path in self.static_images.items():
                if image_path.exists():
                    # Convert to absolute path and use file:// protocol
                    abs_path = image_path.absolute()
                    # Use proper URL encoding for file paths
                    file_url = f"file://{abs_path}"
                    self.base_image_urls[f"{key}_url"] = file_url
                else:
                    # Create placeholder if it doesn't exist
                    self._create_placeholder_image(image_path, key)
                    abs_path = image_path.absolute()
                    file_url = f"file://{abs_path}"
                    self.base_image_urls[f"{key}_url"] = file_url
            
            # Debug: Show all loaded image URLs
            
                
        except Exception as e:
            # Fallback to relative paths
            self.base_image_urls = {
                'vital_insights_logo_url': "static/images/vital_insights_logo.png",
                'fingerprint_icon_url': "static/images/fingerprint_icon.png",
                'body_outline_image_url': "static/images/body_outline.png",
                'ap_spine_placeholder_url': "static/images/ap_spine_placeholder.png",
                'femur_placeholder_url': "static/images/femur_placeholder.png",
                'fat_distribution_placeholder_url': "static/images/fat_distribution_placeholder.png",
            }
    def _setup_static_images(self):
        """Setup static images - create placeholder images if they don't exist"""
        for image_name, image_path in self.static_images.items():
            if not image_path.exists():
                self._create_placeholder_image(image_path, image_name)
    
    def _create_placeholder_image(self, image_path, image_name, size=(200, 100), color=(255, 107, 61)):
        """Create a placeholder image for testing - IMPROVED VERSION"""
        try:
            # Customize placeholder based on image type
            if 'logo' in image_name:
                text = "Vital Insights Logo"
                size = (180, 60)
                color = (255, 107, 61)  # Orange
            elif 'fingerprint' in image_name:
                text = "Fingerprint Icon"
                size = (60, 60)
                color = (255, 107, 61)  # Orange
            elif 'body_outline' in image_name:
                text = "Body Outline"
                size = (130, 280)
                color = (100, 100, 100)  # Gray
            elif 'spine' in image_name:
                text = "AP-Spine"
                size = (90, 130)
                color = (200, 200, 200)  # Light gray
            elif 'femur' in image_name:
                text = "Femur"
                size = (90, 130)
                color = (200, 200, 200)  # Light gray
            elif 'fat' in image_name:
                text = "Fat Distribution"
                size = (80, 120)
                color = (255, 150, 100)  # Light orange
            else:
                text = image_path.stem
                size = (200, 100)
                color = (255, 107, 61)  # Orange
            
            # Create image with white background
            img = PILImage.new('RGB', size, color=(255, 255, 255))
            draw = ImageDraw.Draw(img)
            
            # Draw colored rectangle
            draw.rectangle([5, 5, size[0]-5, size[1]-5], fill=color, outline=(0, 0, 0), width=1)
            
            # Add text
            try:
                # Try to use a font
                font = ImageFont.load_default()
                # Calculate text position
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                x = (size[0] - text_width) // 2
                y = (size[1] - text_height) // 2
                draw.text((x, y), text, fill=(255, 255, 255), font=font)
            except:
                # Fallback without font
                x = size[0] // 4
                y = size[1] // 2 - 10
                draw.text((x, y), text, fill=(255, 255, 255))
            
            # Ensure directory exists
            image_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save as PNG
            img.save(image_path, format='PNG')
            
        except Exception as e:
            st.error(f"❌ Error creating placeholder {image_name}: {str(e)}")

    def _process_uploaded_image(self, uploaded_file, target_width, target_height):
        """Process uploaded image to fit the PDF layout - COMBINED ROBUST VERSION"""
        try:
            if uploaded_file is None:
                return None
            
            # Read and verify image
            image_bytes = uploaded_file.getvalue()
            if not image_bytes:
                return None
            
            # Read image from bytes
            try:
                image = PILImage.open(io.BytesIO(image_bytes))
            except Exception as e:
                return None
            
            # Convert to RGB if necessary
            if image.mode in ('RGBA', 'LA', 'P'):
                background = PILImage.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            elif image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize image to fit the target dimensions while maintaining aspect ratio
            image.thumbnail((target_width, target_height), PILImage.Resampling.LANCZOS)
            
            # Save to temporary file for WeasyPrint
            temp_file = io.BytesIO()
            image.save(temp_file, format='PNG', quality=95)
            temp_file.seek(0)
    
            return temp_file
                
        except Exception as e:
            return None
    def _get_report_images_for_pdf(self, report_id):
        """Get stored images for PDF generation with static fallbacks"""
        conn = get_db_connection()
        if not conn:
            return {}
        
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT image_type, image_data FROM report_images WHERE report_id = %s", (report_id,))
            images = cursor.fetchall()
            
            image_dict = {}
            for img in images:
                if img['image_data']:
                    try:
                        image_data = base64.b64decode(img['image_data'])
                        image_file = io.BytesIO(image_data)
                        image_dict[img['image_type']] = image_file
                    except Exception as e:
                        st.error(f"Error decoding image {img['image_type']}: {str(e)}")
                        image_dict[img['image_type']] = None
            
            return image_dict
        except Exception as e:
            return {}
        finally:
            cursor.close()
            conn.close()
    def show_image_preview_page(image_data, title):
        """Show a full page preview for an image"""
        st.markdown(f"<h1 style='text-align: center;'>🔍 {title}</h1>", unsafe_allow_html=True)
        
        if image_data:
            try:
                # Display the image
                st.image(image_data, use_column_width=True)
                
                # Download button
                st.download_button(
                    label="📥 Download Image",
                    data=image_data.getvalue(),
                    file_name=f"{title.replace(' ', '_')}.jpg",
                    mime="image/jpeg"
                )
            except Exception as e:
                st.error(f"Error displaying image: {str(e)}")
        else:
            st.warning("No image data available")
        
        # Back button
        if st.button("← Back"):
            st.session_state.show_image_preview = False
            st.rerun()
    def _save_report_images(self, report_id, image_data):
        """Save images to database - FIXED"""
        conn = get_db_connection()
        if not conn:
            return False
        
        cursor = conn.cursor()
        try:
            for image_type, image_file in image_data.items():
                if image_file is not None:
                    try:
                        # Get image bytes
                        image_bytes = image_file.getvalue()
                        
                        # Verify it's a valid image
                        try:
                            PILImage.open(io.BytesIO(image_bytes))
                        except Exception as e:
                            continue
                        
                        # Convert to base64
                        image_b64 = base64.b64encode(image_bytes).decode()
                        
                        # Save to database
                        cursor.execute("""
                            INSERT INTO report_images (report_id, image_type, image_data, image_format)
                            VALUES (%s, %s, %s, %s)
                            ON DUPLICATE KEY UPDATE image_data = VALUES(image_data), image_format = VALUES(image_format)
                        """, (report_id, image_type, image_b64, 'JPEG'))
                        
                    except Exception as e:
                        continue
            
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()

    def _generate_assessments(self, report_data):
        """Generate automatic assessments and recommendations matching the exact format"""
        # Ensure all values are float to avoid decimal/float mixing issues
        def safe_float(value):
            if value is None:
                return 0.0
            try:
                if hasattr(value, 'quantize'):
                    return float(value)
                return float(value)
            except (ValueError, TypeError):
                return 0.0
        
        body_fat = safe_float(report_data['body_fat_percentage'])
        muscle_mass = safe_float(report_data['muscle_mass_almi'])
        bone_density = safe_float(report_data['bone_density_t_score'])
        age = safe_float(report_data['age'])
        gender = report_data['gender']
        visceral_fat = safe_float(report_data['visceral_fat_area'])
        ag_ratio = safe_float(report_data['ag_ratio'])
        
        # Body Zone Assessment
        if body_fat > (28 if gender == 'M' else 35) and muscle_mass > 8:
            body_zone = "POWER RESERVE ZONE"
            zone_description = "You've built good muscle but have higher-than-ideal fat levels - an opportunity to fine-tune composition."
        elif body_fat <= (20 if gender == 'M' else 28) and muscle_mass > 9:
            body_zone = "OPTIMAL ZONE"
            zone_description = "You have an excellent balance of muscle mass and body fat - focus on maintaining this healthy composition."
        elif muscle_mass < 8:
            body_zone = "DEVELOPMENT ZONE"
            zone_description = "You have an opportunity to build muscle mass while optimizing body fat levels through structured training."
        else:
            body_zone = "BALANCED ZONE"
            zone_description = "You have a solid foundation with opportunities to optimize your body composition for better health and performance."
        
        # Muscle Assessment
        if muscle_mass >= 7:
            muscle_assessment_title = "ADEQUATELY MUSCLED"
            muscle_assessment_description = f"ALMI: {muscle_mass} kg/m² (Your ALMI is above 7 - an indicator of adequate skeletal muscle health and physical resilience.)"
            muscle_mass_status = "In Range"
        else:
            muscle_assessment_title = "UNDER MUSCLED"
            muscle_assessment_description = f"ALMI: {muscle_mass} kg/m² (Your ALMI is below 7 - indicating an opportunity to build muscle mass for better health and performance.)"
            muscle_mass_status = "Needs Attention"
        
        # Fat Assessment
        body_fat_range = "11.2% - 30.2%" if gender == 'M' else "20.0% - 35.0%"
        if body_fat > (25 if gender == 'M' else 32):
            fat_assessment_title = f"OVER NOURISHED (Body Fat: {body_fat}%)"
            fat_assessment_description = f"For a {age}-year-old {gender.lower()}, your body fat is above the range of {body_fat_range}. This can increase metabolic stress and impact energy, hormones, and recovery. Gradual fat loss may help improve overall health and performance."
            body_fat_status = "Needs Attention"
        else:
            fat_assessment_title = f"HEALTHY BODY FAT (Body Fat: {body_fat}%)"
            fat_assessment_description = f"For a {age}-year-old {gender.lower()}, your body fat is within the healthy range of {body_fat_range}. Maintain this level through balanced nutrition and regular exercise."
            body_fat_status = "In Range"
        
        # Bone Density Status
        if bone_density >= -1.0:
            bone_density_status = "In Range"
        else:
            bone_density_status = "Needs Attention"
        
        # Bone Health Assessment
        if bone_density >= -1.0:
            bone_health_box_class = "box-green"
            bone_health_box_color = "#4CAF50"
            bone_health_title = "✓ YOUR BONES ARE STRONG"
            bone_health_description = "Your bones are well-mineralised and structurally solid - above the threshold for concern."
        elif bone_density >= -2.5:
            bone_health_box_class = "box-yellow"
            bone_health_box_color = "#FFA500"
            bone_health_title = "⚠️ YOUR BONES ARE WEAKENING"
            bone_health_description = "Your bone density indicates osteopenia. This is an early warning sign that your bones are starting to weaken."
        else:
            bone_health_box_class = "box-red"
            bone_health_box_color = "#FF6B3D"
            bone_health_title = "⚠️ YOUR BONES ARE FRAGILE"
            bone_health_description = "Your bone density indicates osteoporosis. Your bones are fragile and more prone to fractures."
        
        # Fat Distribution Assessment
        if body_fat > (25 if gender == 'M' else 32):
            body_fat_box_class = "box-red"
            body_fat_title = "⚠️ YOUR BODY FAT PERCENTAGE IS UNHEALTHY"
            body_fat_description = "Your body fat percentage is above the healthy reference range. While fat is essential for function, excess can increase the risk of insulin resistance, fatigue, and systemic inflammation. Fat loss through strength and endurance training is recommended."
        else:
            body_fat_box_class = "box-green"
            body_fat_title = "✓ YOUR BODY FAT PERCENTAGE IS HEALTHY"
            body_fat_description = "Your body fat percentage is within the healthy reference range. Maintain this level through balanced nutrition and regular exercise."
        
        # Visceral Fat Assessment
        if visceral_fat > 100:
            visceral_fat_box_class = "box-red"
            visceral_fat_title = "⚠️ YOUR VISCERAL FAT AREA IS HIGH"
            visceral_fat_description = "Your visceral fat area exceeds the healthy threshold. Visceral fat is more hormonally active and linked to insulin resistance, inflammation, and cardiovascular risk."
        else:
            visceral_fat_box_class = "box-green"
            visceral_fat_title = "✓ YOUR VISCERAL FAT AREA IS HEALTHY"
            visceral_fat_description = "Your visceral fat area is within the healthy range. Continue maintaining a healthy lifestyle to keep visceral fat at optimal levels."
        
        # A/G Ratio Assessment
        if ag_ratio > 1.0:
            ag_ratio_box_class = "box-yellow"
            ag_ratio_title = "📊 YOUR A/G RATIO IS SUBOPTIMAL"
            ag_ratio_description = f"Your A/G ratio is {ag_ratio}. Your A/G ratio is above 1.0, indicating a higher proportion of upper body fat (Android pattern). This may be associated with increased cardiovascular risk and insulin resistance."
        else:
            ag_ratio_box_class = "box-green"
            ag_ratio_title = "✓ YOUR A/G RATIO IS OPTIMAL"
            ag_ratio_description = f"Your A/G ratio is {ag_ratio}. Your A/G ratio is within the optimal range, indicating a healthy fat distribution pattern."
        
        # Asymmetry Assessment
        arms_asymmetry = abs(safe_float(report_data.get('arms_asymmetry', 0)))
        legs_asymmetry = abs(safe_float(report_data.get('legs_asymmetry', 0)))
        
        if arms_asymmetry < 5 and legs_asymmetry < 5:
            asymmetry_box_class = "box-green"
            asymmetry_box_color = "#4CAF50"
            asymmetry_title = "✓ YOU HAVE NO ASYMMETRY"
            asymmetry_description = "Your muscle distribution is symmetrical, which supports efficient movement and reduces injury risk. This is the ideal zone for long-term performance and joint health."
        elif arms_asymmetry < 10 and legs_asymmetry < 10:
            asymmetry_box_class = "box-yellow"
            asymmetry_box_color = "#FFA500"
            asymmetry_title = "⚠️ MINOR ASYMMETRY DETECTED"
            asymmetry_description = "You have minor asymmetry in muscle distribution. Consider incorporating unilateral exercises to address imbalances and improve movement efficiency."
        else:
            asymmetry_box_class = "box-red"
            asymmetry_box_color = "#FF6B3D"
            asymmetry_title = "⚠️ SIGNIFICANT ASYMMETRY DETECTED"
            asymmetry_description = "You have significant asymmetry in muscle distribution. This may increase injury risk and affect movement efficiency. Focus on unilateral training and consult with a physical therapist if needed."
        
        # Risk Profile Assessment
        risk_factors = 0
        if body_fat > (25 if gender == 'M' else 32):
            risk_factors += 1
        if visceral_fat > 100:
            risk_factors += 1
        if bone_density < -1.0:
            risk_factors += 1
        if muscle_mass < 7:
            risk_factors += 1
        
        if risk_factors >= 3:
            risk_profile_color = "#FF6B3D"
            risk_profile_title = "⚠️ RISK PROFILE IS HIGH"
            unhealthy_fat_title = "⚠️ UNHEALTHY FAT"
            unhealthy_fat_level = "HIGH"
        elif risk_factors >= 2:
            risk_profile_color = "#FFA500"
            risk_profile_title = "⚠️ RISK PROFILE IS MODERATE"
            unhealthy_fat_title = "⚠️ UNHEALTHY FAT"
            unhealthy_fat_level = "MODERATE"
        else:
            risk_profile_color = "#4CAF50"
            risk_profile_title = "✓ RISK PROFILE IS LOW"
            unhealthy_fat_title = "✓ HEALTHY FAT"
            unhealthy_fat_level = "LOW"
        
        return {
            'body_zone': body_zone,
            'zone_description': zone_description,
            'muscle_assessment_title': muscle_assessment_title,
            'muscle_assessment_description': muscle_assessment_description,
            'fat_assessment_title': fat_assessment_title,
            'fat_assessment_description': fat_assessment_description,
            'body_fat_status': body_fat_status,
            'muscle_mass_status': muscle_mass_status,
            'bone_density_status': bone_density_status,
            'bone_health_box_class': bone_health_box_class,
            'bone_health_box_color': bone_health_box_color,
            'bone_health_title': bone_health_title,
            'bone_health_description': bone_health_description,
            'body_fat_box_class': body_fat_box_class,
            'body_fat_title': body_fat_title,
            'body_fat_description': body_fat_description,
            'visceral_fat_box_class': visceral_fat_box_class,
            'visceral_fat_title': visceral_fat_title,
            'visceral_fat_description': visceral_fat_description,
            'ag_ratio_box_class': ag_ratio_box_class,
            'ag_ratio_title': ag_ratio_title,
            'ag_ratio_description': ag_ratio_description,
            'asymmetry_box_class': asymmetry_box_class,
            'asymmetry_box_color': asymmetry_box_color,
            'asymmetry_title': asymmetry_title,
            'asymmetry_description': asymmetry_description,
            'risk_profile_color': risk_profile_color,
            'risk_profile_title': risk_profile_title,
            'unhealthy_fat_title': unhealthy_fat_title,
            'unhealthy_fat_level': unhealthy_fat_level
        }

    def _generate_recommendations(self, report_data):
        """Generate automatic nutrition and training recommendations matching the exact format"""
        # Ensure all values are float to avoid decimal/float mixing issues
        def safe_float(value):
            if value is None:
                return 0.0
            try:
                if hasattr(value, 'quantize'):
                    return float(value)
                return float(value)
            except (ValueError, TypeError):
                return 0.0
        
        body_fat = safe_float(report_data['body_fat_percentage'])
        muscle_mass = safe_float(report_data['muscle_mass_almi'])
        bone_density = safe_float(report_data['bone_density_t_score'])
        visceral_fat = safe_float(report_data['visceral_fat_area'])
        total_mass = safe_float(report_data['total_mass'])
        gender = report_data['gender']
        
        nutrition_recommendations = []
        training_recommendations = []
        
        # Nutrition recommendations
        if body_fat > (28 if gender == 'M' else 35):
            nutrition_recommendations.append("Calorie Restriction - You are consuming more calories than your body needs, leading to excess fat storage. Lower your Carbohydrate & Processed food intake.")
        elif body_fat > (25 if gender == 'M' else 32):
            nutrition_recommendations.append("Moderate Calorie Restriction - Focus on whole foods and reduce processed carbohydrates to optimize body composition.")
        else:
            nutrition_recommendations.append("Maintenance Calories - Your body fat is within a healthy range. Focus on nutrient-dense foods and balanced macronutrients.")
        
        # Protein recommendations
        protein_multiplier = 1.6 if muscle_mass < 8.5 else (1.4 if muscle_mass > 11 else 1.5)
        protein_need = round(total_mass * protein_multiplier, 1)
        nutrition_recommendations.append(f"Protein Intake - Consume {protein_need}g of protein daily ({protein_multiplier}g per kg) to support muscle maintenance and metabolism.")
        
        # Visceral fat specific
        if visceral_fat > 100:
            nutrition_recommendations.append("Reduce Saturated Fat - Limit intake of ghee, butter, meats, coconut oil, and fried foods to manage visceral fat accumulation.")
        
        # Training recommendations
        if body_fat > (25 if gender == 'M' else 32):
            cardio_minutes = "200-250" if body_fat > (30 if gender == 'M' else 35) else "150-180"
            training_recommendations.append(f"Zone 2 Cardio - Include {cardio_minutes} minutes weekly of moderate-intensity aerobic exercise at 70-75% of maximum heart rate for optimal fat loss.")
        
        # Strength training
        if muscle_mass < 8.5:
            training_recommendations.append("Strength Training Priority - Focus on compound exercises 3-4 times weekly with progressive overload to build lean muscle mass.")
        elif muscle_mass > 11:
            training_recommendations.append("Maintenance Strength - Continue resistance training 2-3 times weekly to maintain your excellent muscle mass.")
        else:
            training_recommendations.append("Progressive Strength Training - Include resistance training 3 times weekly with gradual progression for optimal muscle maintenance.")
        
        # Bone health
        if bone_density < -1.0:
            training_recommendations.append("Weight-Bearing Exercise - Include impact exercises and resistance training to support bone mineral density.")
        
        return {
            'nutrition_recommendations': nutrition_recommendations,
            'training_recommendations': training_recommendations
        }

    def _calculate_regional_totals(self, report_data):
        """Calculate regional totals and percentages for the asymmetry page matching exact format"""
        # Ensure all values are float to avoid decimal/float mixing issues
        def safe_float(value):
            if value is None:
                return 0.0
            try:
                if hasattr(value, 'quantize'):
                    return float(value)
                return float(value)
            except (ValueError, TypeError):
                return 0.0
        
        # Calculate arm totals
        right_arm_total = safe_float(report_data.get('right_arm_fat', 0)) + safe_float(report_data.get('right_arm_lean', 0)) + safe_float(report_data.get('right_arm_bmc', 0))
        left_arm_total = safe_float(report_data.get('left_arm_fat', 0)) + safe_float(report_data.get('left_arm_lean', 0)) + safe_float(report_data.get('left_arm_bmc', 0))
        
        # Calculate leg totals
        right_leg_total = safe_float(report_data.get('right_leg_fat', 0)) + safe_float(report_data.get('right_leg_lean', 0)) + safe_float(report_data.get('right_leg_bmc', 0))
        left_leg_total = safe_float(report_data.get('left_leg_fat', 0)) + safe_float(report_data.get('left_leg_lean', 0)) + safe_float(report_data.get('left_leg_bmc', 0))
        
        # Calculate trunk total
        trunk_total = safe_float(report_data.get('trunk_fat', 0)) + safe_float(report_data.get('trunk_lean', 0)) + safe_float(report_data.get('trunk_bmc', 0))
        
        # Calculate percentages for trunk composition
        trunk_fat_percent = round((safe_float(report_data.get('trunk_fat', 0)) / trunk_total) * 100) if trunk_total > 0 else 0
        trunk_lean_percent = round((safe_float(report_data.get('trunk_lean', 0)) / trunk_total) * 100) if trunk_total > 0 else 0
        trunk_bone_percent = round((safe_float(report_data.get('trunk_bmc', 0)) / trunk_total) * 100) if trunk_total > 0 else 0
        
        # Calculate percentages for right arm composition
        right_arm_fat_percent = round((safe_float(report_data.get('right_arm_fat', 0)) / right_arm_total) * 100) if right_arm_total > 0 else 0
        right_arm_muscle_percent = round((safe_float(report_data.get('right_arm_lean', 0)) / right_arm_total) * 100) if right_arm_total > 0 else 0
        right_arm_bone_percent = round((safe_float(report_data.get('right_arm_bmc', 0)) / right_arm_total) * 100) if right_arm_total > 0 else 0
        
        # Calculate percentages for left arm composition
        left_arm_fat_percent = round((safe_float(report_data.get('left_arm_fat', 0)) / left_arm_total) * 100) if left_arm_total > 0 else 0
        left_arm_muscle_percent = round((safe_float(report_data.get('left_arm_lean', 0)) / left_arm_total) * 100) if left_arm_total > 0 else 0
        left_arm_bone_percent = round((safe_float(report_data.get('left_arm_bmc', 0)) / left_arm_total) * 100) if left_arm_total > 0 else 0
        
        # Calculate percentages for right leg composition
        right_leg_fat_percent = round((safe_float(report_data.get('right_leg_fat', 0)) / right_leg_total) * 100) if right_leg_total > 0 else 0
        right_leg_muscle_percent = round((safe_float(report_data.get('right_leg_lean', 0)) / right_leg_total) * 100) if right_leg_total > 0 else 0
        right_leg_bone_percent = round((safe_float(report_data.get('right_leg_bmc', 0)) / right_leg_total) * 100) if right_leg_total > 0 else 0
        
        # Calculate percentages for left leg composition
        left_leg_fat_percent = round((safe_float(report_data.get('left_leg_fat', 0)) / left_leg_total) * 100) if left_leg_total > 0 else 0
        left_leg_muscle_percent = round((safe_float(report_data.get('left_leg_lean', 0)) / left_leg_total) * 100) if left_leg_total > 0 else 0
        left_leg_bone_percent = round((safe_float(report_data.get('left_leg_bmc', 0)) / left_leg_total) * 100) if left_leg_total > 0 else 0
        
        # Calculate asymmetry percentages
        arms_asymmetry = round(((right_arm_total - left_arm_total) / ((right_arm_total + left_arm_total) / 2)) * 100, 2) if (right_arm_total + left_arm_total) > 0 else 0
        legs_asymmetry = round(((right_leg_total - left_leg_total) / ((right_leg_total + left_leg_total) / 2)) * 100, 2) if (right_leg_total + left_leg_total) > 0 else 0
        
        return {
            'right_arm_total': round(right_arm_total, 2),
            'left_arm_total': round(left_arm_total, 2),
            'right_leg_total': round(right_leg_total, 2),
            'left_leg_total': round(left_leg_total, 2),
            'trunk_total': round(trunk_total, 2),
            'trunk_fat_percent': trunk_fat_percent,
            'trunk_lean_percent': trunk_lean_percent,
            'trunk_muscle_percent': trunk_lean_percent,  # Add alias for template compatibility
            'trunk_bone_percent': trunk_bone_percent,
            'right_arm_fat_percent': right_arm_fat_percent,
            'right_arm_muscle_percent': right_arm_muscle_percent,
            'right_arm_bone_percent': right_arm_bone_percent,
            'left_arm_fat_percent': left_arm_fat_percent,
            'left_arm_muscle_percent': left_arm_muscle_percent,
            'left_arm_bone_percent': left_arm_bone_percent,
            'right_leg_fat_percent': right_leg_fat_percent,
            'right_leg_muscle_percent': right_leg_muscle_percent,
            'right_leg_bone_percent': right_leg_bone_percent,
            'left_leg_fat_percent': left_leg_fat_percent,
            'left_leg_muscle_percent': left_leg_muscle_percent,
            'left_leg_bone_percent': left_leg_bone_percent,
            'arms_asymmetry': arms_asymmetry,
            'legs_asymmetry': legs_asymmetry,
            'right_arm_fat_g': int(safe_float(report_data.get('right_arm_fat', 0)) * 1000),
            'right_arm_lean_g': int(safe_float(report_data.get('right_arm_lean', 0)) * 1000),
            'right_arm_bmc_g': int(safe_float(report_data.get('right_arm_bmc', 0)) * 1000),
            'left_arm_fat_g': int(safe_float(report_data.get('left_arm_fat', 0)) * 1000),
            'left_arm_lean_g': int(safe_float(report_data.get('left_arm_lean', 0)) * 1000),
            'left_arm_bmc_g': int(safe_float(report_data.get('left_arm_bmc', 0)) * 1000),
            'right_leg_fat_g': int(safe_float(report_data.get('right_leg_fat', 0)) * 1000),
            'right_leg_lean_g': int(safe_float(report_data.get('right_leg_lean', 0)) * 1000),
            'right_leg_bmc_g': int(safe_float(report_data.get('right_leg_bmc', 0)) * 1000),
            'left_leg_fat_g': int(safe_float(report_data.get('left_leg_fat', 0)) * 1000),
            'left_leg_lean_g': int(safe_float(report_data.get('left_leg_lean', 0)) * 1000),
            'left_leg_bmc_g': int(safe_float(report_data.get('left_leg_bmc', 0)) * 1000),
        }
    def verify_static_images(self):
        """Verify that all static images exist and are accessible"""
        missing_images = []
        for image_name, image_path in self.static_images.items():
            if image_path.exists():
                file_size = image_path.stat().st_size
            else:
                missing_images.append(image_name)
        
        if missing_images:
            for missing in missing_images:
                self._create_placeholder_image(self.static_images[missing], missing)
        
        # Verify base URLs
        for key, url in self.base_image_urls.items():
            pass
    def generate_pdf(self, report_data, page_size='A4'):
        """Generate exact PDF replica using WeasyPrint - FIXED IMAGE HANDLING"""
        try:
            # Convert all decimal values to float
            def convert_to_float(value):
                if value is None:
                    return 0.0
                try:
                    if hasattr(value, 'quantize'):
                        return float(value)
                    return float(value)
                except (ValueError, TypeError):
                    return 0.0
            
            # Convert all numeric values in report_data to float
            converted_report_data = {}
            for key, value in report_data.items():
                if isinstance(value, (int, float, str)) and str(value).replace('.', '').replace('-', '').isdigit():
                    converted_report_data[key] = convert_to_float(value)
                else:
                    converted_report_data[key] = value
            
            report_data = converted_report_data
            
            # Debug: Check static images
            # Get uploaded images from database
            stored_images = self._get_report_images_for_pdf(report_data['report_id'])
            
            # Use proper image URLs - FIXED
            image_urls = {}
            for img_type in ['ap_spine', 'right_femur', 'left_femur', 'body_outline', 'fat_distribution']:
                if stored_images.get(img_type):
                    try:
                        # Save image to temporary file with proper extension
                        temp_dir = tempfile.gettempdir()
                        temp_path = os.path.join(temp_dir, f"{img_type}_{report_data['report_id']}.png")
                        
                        with open(temp_path, 'wb') as f:
                            f.write(stored_images[img_type].getvalue())
                        
                        # Use absolute file path with file:// protocol
                        image_urls[img_type] = f"file://{os.path.abspath(temp_path)}"
                        
                    except Exception as e:
                        # Fallback to placeholder
                        placeholder_key = f'{img_type}_placeholder_url'
                        image_urls[img_type] = self.base_image_urls.get(placeholder_key, self.base_image_urls['ap_spine_placeholder_url'])
                else:
                    # Use placeholder image
                    placeholder_key = f'{img_type}_placeholder_url'
                    if placeholder_key in self.base_image_urls:
                        image_urls[img_type] = self.base_image_urls[placeholder_key]
                    else:
                        # Final fallback
                        image_urls[img_type] = self.base_image_urls['ap_spine_placeholder_url']
            
            # Generate assessments and recommendations
            assessments = self._generate_assessments(report_data)
            recommendations = self._generate_recommendations(report_data)
            regional_data = self._calculate_regional_totals(report_data)
            
            # Prepare template data with FIXED image URLs
            template_data = {
                'patient_name': report_data.get('patient_name', 'BRI.K'),
                'patient_id': report_data.get('patient_id', '000480'),
                'report_id': report_data.get('report_id', '000653'),
                'report_date': report_data.get('report_date', '17 SEP 2025'),
                'age': report_data.get('age', 36),
                'gender': report_data.get('gender', 'M'),
                'height': report_data.get('height', 171),
                'total_mass': report_data.get('total_mass', 104.6),
                'fat_mass': report_data.get('fat_mass', 39.79),
                'lean_mass': report_data.get('lean_mass', 61.84),
                'bone_mass': report_data.get('bone_mass', 2.94),
                'body_fat_percentage': report_data.get('body_fat_percentage', 38.0),
                'muscle_mass_almi': report_data.get('muscle_mass_almi', 10.23),
                'bone_density_t_score': report_data.get('bone_density_t_score', -0.6),
                'visceral_fat_area': report_data.get('visceral_fat_area', 170.0),
                'ag_ratio': report_data.get('ag_ratio', 1.23),
                'ffmi': report_data.get('ffmi', 20.67),
                'fracture_risk': report_data.get('fracture_risk', 'LOW'),
                'muscle_loss_risk': report_data.get('muscle_loss_risk', 'LOW'),
                'z_score': report_data.get('z_score', -0.6),
                
                # Image URLs - FIXED: Use proper URLs
                'vital_insights_logo_url': self.base_image_urls['vital_insights_logo_url'],
                'fingerprint_icon_url': self.base_image_urls['fingerprint_icon_url'],
               
                
                # Use uploaded images if available, otherwise static placeholders
                'body_outline_image_url': image_urls.get('body_outline_image_url'),
                'ap_spine_image_url': image_urls.get('ap_spine'),
                'right_femur_image_url': image_urls.get('right_femur'),
                'left_femur_image_url': image_urls.get('left_femur'),
                'fat_distribution_image_url': image_urls.get('fat_distribution'),
                
                # Measurements data
                'ap_spine_measurements': report_data.get('ap_spine_measurements', [
                    {'region': 'L1', 'bmd': '1.213', 't_score': '0.6', 'z_score': '0.3'},
                    {'region': 'L2', 'bmd': '1.257', 't_score': '0.4', 'z_score': '0.1'},
                    {'region': 'L3', 'bmd': '1.42', 't_score': '1.6', 'z_score': '1.3'},
                    {'region': 'L4', 'bmd': '1.47', 't_score': '1.5', 'z_score': '1.2'},
                    {'region': 'L1-L4', 'bmd': '1.329', 't_score': '1.1', 'z_score': '0.8'}
                ]),
                'right_femur_measurements': report_data.get('right_femur_measurements', [
                    {'region': 'NECK', 'bmd': '0.961', 't_score': '-0.6', 'z_score': '-0.6'},
                    {'region': 'TOTAL', 'bmd': '0.995', 't_score': '-0.1', 'z_score': '-0.6'}
                ]),
                'left_femur_measurements': report_data.get('left_femur_measurements', [
                    {'region': 'NECK', 'bmd': '1.047', 't_score': '0.1', 'z_score': '0.0'},
                    {'region': 'TOTAL', 'bmd': '1.064', 't_score': '0.4', 'z_score': '-0.1'}
                ]),
                
                **assessments,
                **recommendations,
                **regional_data
            }
            
            # Debug: Check if images are properly formatted
            
            image_count = 0
            #
           
            
            # Render HTML template
            html_content = self.html_template.render(**template_data)
            
            # Generate PDF with WeasyPrint - FIXED: Add better error handling
            try:
               
                html = weasyprint.HTML(string=html_content, base_url="D:/dexa-report-system/static")
                
                # Configure PDF options based on page size
                if page_size == 'A4':
                    pdf_bytes = html.write_pdf()
                else:
                    pdf_bytes = html.write_pdf(stylesheets=[weasyprint.CSS(string='@page { size: A5; }')])
                return pdf_bytes
                
            except Exception as e:
                # Fallback: Create a simple PDF with error message
                try:
                    from reportlab.pdfgen import canvas
                    from reportlab.lib.pagesizes import letter
                    
                    buffer = io.BytesIO()
                    p = canvas.Canvas(buffer, pagesize=letter)
                    p.drawString(100, 750, "DEXA Report - PDF Generation Error")
                    p.drawString(100, 730, f"Error: {str(e)}")
                    p.drawString(100, 710, "Please check the image files and try again.")
                    p.save()
                    buffer.seek(0)
                    return buffer.getvalue()
                except:
                    return None
                
        except Exception as e:
            return None 
    def _get_report_images_for_pdf(self, report_id):
        """Get stored images for PDF generation with proper file handling"""
        conn = get_db_connection()
        if not conn:
            return {}
        
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT image_type, image_data FROM report_images WHERE report_id = %s", (report_id,))
            images = cursor.fetchall()
            
            image_dict = {}
            for img in images:
                if img['image_data']:
                    try:
                        # Decode base64 image data
                        image_data = base64.b64decode(img['image_data'])
                        
                        # Create BytesIO object
                        image_file = io.BytesIO(image_data)
                        
                        # Verify it's a valid image
                        try:
                            pil_image = PILImage.open(image_file)
                            # Reset stream position
                            image_file.seek(0)
                            image_dict[img['image_type']] = image_file
                        except Exception as e:
                            image_dict[img['image_type']] = None
                            
                    except Exception as e:
                        image_dict[img['image_type']] = None
            
            return image_dict
        except Exception as e:
            return {}
        finally:
            cursor.close()
            conn.close()
    def save_to_supabase_storage(self, pdf_bytes, filename, report_id, file_format):
        """Save PDF to Supabase storage"""
        success, result, file_url, unique_filename = self.supabase_storage.upload_pdf_to_supabase(
            pdf_bytes, filename, report_id, file_format
        )
        return success

    def list_stored_reports(self):
        """List all stored reports in Supabase storage"""
        return self.supabase_storage.list_supabase_files()
    
    def get_storage_info(self):
        """Get storage usage information"""
        return self.supabase_storage.get_storage_info()

# =============================================================================
# SUPABASE CLOUD STORAGE MANAGEMENT
# =============================================================================

class SupabaseStorageManager:
    def __init__(self):
        self.supabase_url = st.secrets["SUPABASE_URL"]
        self.supabase_key = st.secrets.get("SUPABASE_SERVICE_ROLE_KEY", st.secrets["SUPABASE_KEY"])
        self.supabase = create_client(self.supabase_url, self.supabase_key)
        self.bucket_name = "pdf_reports"
        self.setup_supabase_storage()
    
    def setup_supabase_storage(self):
        """Setup Supabase storage bucket"""
        try:
            # Check if bucket exists, create if not
            buckets = self.supabase.storage.list_buckets()
            bucket_names = [bucket.name for bucket in buckets]
            
            if self.bucket_name not in bucket_names:
                # Create bucket with proper configuration
                result = self.supabase.storage.create_bucket(
                    self.bucket_name,
                    options={
                        "public": False,
                        "allowed_mime_types": ["application/pdf"],
                        "file_size_limit": 10485760,  # 10MB limit
                    }
                )
            else:
                pass
                
        except Exception as e:
            st.error(f"Error setting up Supabase storage: {str(e)}")
    
    def upload_pdf_to_supabase(self, pdf_bytes, filename, report_id, file_format):
        """Upload PDF to Supabase storage"""
        try:
            # Generate unique filename to avoid conflicts
            unique_filename = f"{uuid.uuid4()}_{filename}"
            
            # Upload file
            result = self.supabase.storage.from_(self.bucket_name).upload(
                unique_filename,
                pdf_bytes,
                {"content-type": "application/pdf"}
            )
            
            if result and not hasattr(result, 'error'):
                # Get public URL
                try:
                    file_url = self.supabase.storage.from_(self.bucket_name).get_public_url(unique_filename)
                except:
                    # If bucket is private, create a signed URL
                    signed_url = self.supabase.storage.from_(self.bucket_name).create_signed_url(unique_filename, 3600)
                    file_url = signed_url.signed_url if signed_url else f"Private file: {unique_filename}"
                
                file_size_kb = len(pdf_bytes) / 1024
                
                # Store file metadata in database
                conn = get_db_connection()
                if conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO supabase_files (report_id, filename, unique_filename, file_url, file_size_kb, file_format, uploaded_by)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (report_id, filename, unique_filename, file_url, file_size_kb, file_format, st.session_state.user['user_id']))
                    conn.commit()
                    cursor.close()
                    conn.close()
                
                return True, file_size_kb, file_url, unique_filename
            
            return False, f"Upload failed: {getattr(result, 'error', 'Unknown error')}", None, None
            
        except Exception as e:
            return False, str(e), None, None
    
    def list_supabase_files(self):
        """List all files in Supabase storage"""
        try:
            conn = get_db_connection()
            if not conn:
                return []
            
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT sf.*, r.report_id, p.first_name, p.last_name
                FROM supabase_files sf
                JOIN dexa_reports r ON sf.report_id = r.report_id
                JOIN patients p ON r.patient_id = p.patient_id
                ORDER BY sf.created_at DESC
            """)
            files = cursor.fetchall()
            cursor.close()
            conn.close()
            
            return files
        except Exception as e:
            return []
    
    def delete_supabase_file(self, unique_filename):
        """Delete file from Supabase storage"""
        try:
            result = self.supabase.storage.from_(self.bucket_name).remove([unique_filename])
            
            # Also delete from database
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM supabase_files WHERE unique_filename = %s", (unique_filename,))
                conn.commit()
                cursor.close()
                conn.close()
            
            return True
        except Exception as e:
            return False
    
    def get_storage_info(self):
        """Get storage usage information"""
        try:
            files = self.list_supabase_files()
            total_size_mb = sum(file['file_size_kb'] for file in files) / 1024
            return len(files), total_size_mb
        except Exception as e:
            return 0, 0

# =============================================================================
# DATABASE CONFIGURATION - UPDATED SCHEMA
# =============================================================================

def get_db_connection(max_retries=3):
    """Get MySQL database connection with retry logic"""
    for attempt in range(max_retries):
        try:
            conn = mysql.connector.connect(
                host=st.secrets["MYSQL_HOST"],
                user=st.secrets["MYSQL_USER"],
                password=st.secrets["MYSQL_PASSWORD"],
                database=st.secrets["MYSQL_DATABASE"],
                port=st.secrets.get("MYSQL_PORT", 3306),
                autocommit=False,  # Explicitly manage transactions
                pool_size=5,  # Add connection pooling
                pool_reset_session=True
            )
            return conn
        except mysql.connector.Error as e:
            if attempt < max_retries - 1:
                time.sleep(2)  # Wait before retry
            else:
                return None

def optimize_database_connections():
    """Optimize database settings to prevent lock timeouts"""
    conn = get_db_connection()
    if not conn:
        return
    
    cursor = conn.cursor()
    try:
        # Optimize MySQL settings for better concurrency
        cursor.execute("SET SESSION innodb_lock_wait_timeout = 30")
        cursor.execute("SET SESSION wait_timeout = 60")
        cursor.execute("SET SESSION interactive_timeout = 60")
        conn.commit()
    except Exception as e:
        pass
    finally:
        cursor.close()
        conn.close()

def init_database():
    """Initialize all database tables with required columns"""
    optimize_database_connections()
    
    conn = get_db_connection()
    if not conn:
        return False
        
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS hospitals (
                hospital_id VARCHAR(255) PRIMARY KEY,
                hospital_name VARCHAR(255) NOT NULL,
                hospital_code VARCHAR(50) UNIQUE NOT NULL,
                address TEXT,
                phone_number VARCHAR(20),
                email VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Users table for authentication
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id VARCHAR(255) PRIMARY KEY,
                hospital_id VARCHAR(255),
                username VARCHAR(255) UNIQUE,
                password_hash TEXT,
                user_type ENUM('admin', 'user'),
                full_name TEXT,
                mobile_number VARCHAR(20),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (hospital_id) REFERENCES hospitals(hospital_id)
            )
        """)
        
        # Patient-user mapping for access control
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS patient_user_mapping (
                mapping_id INT AUTO_INCREMENT PRIMARY KEY,
                patient_id VARCHAR(255),
                user_id VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                UNIQUE(patient_id, user_id)
            )
        """)
        
        # Patients table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS patients (
                patient_id VARCHAR(255) PRIMARY KEY,
                hospital_id VARCHAR(255),
                first_name TEXT,
                last_name TEXT,
                age INT,
                gender ENUM('M', 'F'),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (hospital_id) REFERENCES hospitals(hospital_id)
            )
        """)
        
        # Main DEXA reports table - UPDATED WITH NEW FIELDS
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dexa_reports (
                report_id VARCHAR(255) PRIMARY KEY,
                patient_id VARCHAR(255),
                hospital_id VARCHAR(255),
                report_date DATE,
                height DECIMAL(10,2),
                total_mass DECIMAL(10,2),
                fat_mass DECIMAL(10,2),
                lean_mass DECIMAL(10,2),
                bone_mass DECIMAL(10,2),
                body_fat_percentage DECIMAL(10,2),
                muscle_mass_almi DECIMAL(10,2),
                bone_density_t_score DECIMAL(10,2),
                z_score DECIMAL(10,2),
                visceral_fat_area DECIMAL(10,2),
                ag_ratio DECIMAL(10,2),
                ffmi DECIMAL(10,2),
                fracture_risk TEXT,
                muscle_loss_risk TEXT,
                
                -- New fields for detailed composition
                right_arm_fat DECIMAL(10,2),
                right_arm_lean DECIMAL(10,2),
                right_arm_bmc DECIMAL(10,2),
                left_arm_fat DECIMAL(10,2),
                left_arm_lean DECIMAL(10,2),
                left_arm_bmc DECIMAL(10,2),
                right_leg_fat DECIMAL(10,2),
                right_leg_lean DECIMAL(10,2),
                right_leg_bmc DECIMAL(10,2),
                left_leg_fat DECIMAL(10,2),
                left_leg_lean DECIMAL(10,2),
                left_leg_bmc DECIMAL(10,2),
                trunk_fat DECIMAL(10,2),
                trunk_lean DECIMAL(10,2),
                trunk_bmc DECIMAL(10,2),
                
                -- Image fields (store as base64 or file paths)
                ap_spine_image LONGTEXT,
                right_femur_image LONGTEXT,
                left_femur_image LONGTEXT,
                full_body_image LONGTEXT,
                
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_edited TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                edit_count INT DEFAULT 0,
                created_by VARCHAR(255),
                is_published BOOLEAN DEFAULT FALSE,
                published_at TIMESTAMP NULL,
                FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
                FOREIGN KEY (hospital_id) REFERENCES hospitals(hospital_id)
            )
        """)
        
        # AP-Spine measurements table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ap_spine_measurements (
                measurement_id INT AUTO_INCREMENT PRIMARY KEY,
                report_id VARCHAR(255),
                region VARCHAR(10),
                bmd DECIMAL(10,3),
                t_score DECIMAL(10,2),
                z_score DECIMAL(10,2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (report_id) REFERENCES dexa_reports(report_id)
            )
        """)
        
        # Femur measurements table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS femur_measurements (
                measurement_id INT AUTO_INCREMENT PRIMARY KEY,
                report_id VARCHAR(255),
                side ENUM('RIGHT', 'LEFT'),
                region VARCHAR(50),
                bmd DECIMAL(10,3),
                t_score DECIMAL(10,2),
                z_score DECIMAL(10,2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (report_id) REFERENCES dexa_reports(report_id)
            )
        """)
        
        # Image storage table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS report_images (
                image_id INT AUTO_INCREMENT PRIMARY KEY,
                report_id VARCHAR(255),
                image_type ENUM('ap_spine', 'right_femur', 'left_femur', 'full_body', 'fat_distribution'),
                image_data LONGTEXT,
                image_format VARCHAR(10),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (report_id) REFERENCES dexa_reports(report_id)
            )
        """)
        
        # Version control for reports
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS report_versions (
                version_id INT AUTO_INCREMENT PRIMARY KEY,
                report_id VARCHAR(255),
                version_number INT,
                report_data JSON,
                edited_by VARCHAR(255),
                edit_reason TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (report_id) REFERENCES dexa_reports(report_id)
            )
        """)
        
        # Cloud storage tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS supabase_files (
                file_id INT AUTO_INCREMENT PRIMARY KEY,
                report_id VARCHAR(255),
                filename VARCHAR(255),
                unique_filename VARCHAR(255),
                file_url TEXT,
                file_size_kb DECIMAL(10,2),
                file_format ENUM('A4', 'A5'),
                uploaded_by VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (report_id) REFERENCES dexa_reports(report_id)
            )
        """)
        
        # Create default admin user
        conn.commit()
        return True
        
    except Exception as e:
        return False
    finally:
        cursor.close()
        conn.close()

def update_database_schema():
    """Update existing database schema to add missing columns"""
    conn = get_db_connection()
    if not conn:
        return False
        
    cursor = conn.cursor()
    
    try:
        # List of new columns to add to dexa_reports table
        new_columns = [
            'height DECIMAL(10,2) DEFAULT 0',
            'z_score DECIMAL(10,2) DEFAULT 0',
            'right_arm_fat DECIMAL(10,2) DEFAULT 0',
            'right_arm_lean DECIMAL(10,2) DEFAULT 0',
            'right_arm_bmc DECIMAL(10,2) DEFAULT 0',
            'left_arm_fat DECIMAL(10,2) DEFAULT 0',
            'left_arm_lean DECIMAL(10,2) DEFAULT 0',
            'left_arm_bmc DECIMAL(10,2) DEFAULT 0',
            'right_leg_fat DECIMAL(10,2) DEFAULT 0',
            'right_leg_lean DECIMAL(10,2) DEFAULT 0',
            'right_leg_bmc DECIMAL(10,2) DEFAULT 0',
            'left_leg_fat DECIMAL(10,2) DEFAULT 0',
            'left_leg_lean DECIMAL(10,2) DEFAULT 0',
            'left_leg_bmc DECIMAL(10,2) DEFAULT 0',
            'trunk_fat DECIMAL(10,2) DEFAULT 0',
            'trunk_lean DECIMAL(10,2) DEFAULT 0',
            'trunk_bmc DECIMAL(10,2) DEFAULT 0',
            'ap_spine_image LONGTEXT',
            'right_femur_image LONGTEXT',
            'left_femur_image LONGTEXT',
            'full_body_image LONGTEXT'
        ]
        
        # Check and add each column if it doesn't exist
        for column_def in new_columns:
            column_name = column_def.split(' ')[0]
            try:
                cursor.execute(f"ALTER TABLE dexa_reports ADD COLUMN {column_def}")
            except mysql.connector.Error as e:
                if "Duplicate column name" in str(e):
                    # Column already exists, skip
                    pass
                else:
                    st.warning(f"Could not add column {column_name}: {e}")
        
        # Create measurement tables if they don't exist
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ap_spine_measurements (
                    measurement_id INT AUTO_INCREMENT PRIMARY KEY,
                    report_id VARCHAR(255),
                    region VARCHAR(10),
                    bmd DECIMAL(10,3),
                    t_score DECIMAL(10,2),
                    z_score DECIMAL(10,2),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (report_id) REFERENCES dexa_reports(report_id)
                )
            """)
        except mysql.connector.Error as e:
            pass
        
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS femur_measurements (
                    measurement_id INT AUTO_INCREMENT PRIMARY KEY,
                    report_id VARCHAR(255),
                    side ENUM('RIGHT', 'LEFT'),
                    region VARCHAR(50),
                    bmd DECIMAL(10,3),
                    t_score DECIMAL(10,2),
                    z_score DECIMAL(10,2),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (report_id) REFERENCES dexa_reports(report_id)
                )
            """)
        except mysql.connector.Error as e:
            pass
        
        # Create image storage table if it doesn't exist
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS report_images (
                    image_id INT AUTO_INCREMENT PRIMARY KEY,
                    report_id VARCHAR(255),
                    image_type ENUM('ap_spine', 'right_femur', 'left_femur', 'full_body', 'fat_distribution'),
                    image_data LONGTEXT,
                    image_format VARCHAR(10),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (report_id) REFERENCES dexa_reports(report_id)
                )
            """)
        except mysql.connector.Error as e:
            pass
        
        conn.commit()
        return True
        
    except Exception as e:
        return False
    finally:
        cursor.close()
        conn.close()
# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """Validate phone number (10 digits)"""
    pattern = r'^\d{10}$'
    return re.match(pattern, phone) is not None

def validate_password(password):
    """Validate password (6 or more characters)"""
    return len(password) >= 6
# =============================================================================
# AUTHENTICATION & USER MANAGEMENT
# =============================================================================

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate_user(username, password):
    """Authenticate user credentials"""
    conn = get_db_connection()
    if not conn:
        return None
    
    cursor = conn.cursor(dictionary=True)
    try:
        password_hash = hash_password(password)
        cursor.execute("""
             SELECT u.user_id, u.username, u.user_type, u.full_name, u.hospital_id, 
                   h.hospital_name, h.address, h.phone_number, h.email
            FROM users u 
            LEFT JOIN hospitals h ON u.hospital_id = h.hospital_id
            WHERE u.username = %s AND u.password_hash = %s
        """, (username, password_hash))
        
        user = cursor.fetchone()
        return user
    except Exception as e:
        return None
    finally:
        cursor.close()
        conn.close()

def create_hospital(hospital_data):
    """Create new hospital"""
    conn = get_db_connection()
    if not conn:
        return False
    
    cursor = conn.cursor()
    try:
        hospital_id = f"hosp_{uuid.uuid4().hex[:8]}"
        cursor.execute("""
            INSERT INTO hospitals (hospital_id, hospital_name, hospital_code, address, phone_number, email)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (hospital_id, hospital_data['hospital_name'], hospital_data['hospital_code'], 
              hospital_data['address'], hospital_data['phone_number'], hospital_data['email']))
        
        conn.commit()
        return hospital_id
    except Exception as e:
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def create_user(user_data):
    """Create new user"""
    conn = get_db_connection()
    if not conn:
        return False
    
    cursor = conn.cursor()
    try:
        user_id = f"user_{uuid.uuid4().hex[:8]}"
        password_hash = hash_password(user_data['password'])
        cursor.execute("""
            INSERT INTO users (user_id, hospital_id, username, password_hash, user_type, full_name, mobile_number)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (user_id, user_data['hospital_id'], user_data['username'], password_hash, 
              user_data['user_type'], user_data['full_name'], user_data['mobile_number']))
        
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def link_patient_to_user(patient_id, user_id):
    """Link patient to user for access control"""
    conn = get_db_connection()
    if not conn:
        return False
    
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT IGNORE INTO patient_user_mapping (patient_id, user_id)
            VALUES (%s, %s)
        """, (patient_id, user_id))
        
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error linking patient to user: {str(e)}")
        return False
    finally:
        cursor.close()
        conn.close()

def get_all_patients():
    """Get all patients for admin management"""
    conn = get_db_connection()
    if not conn:
        return []
    
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT patient_id, first_name, last_name, age, gender FROM patients ORDER BY created_at DESC")
        patients = cursor.fetchall()
        return patients
    except Exception as e:
        return []
    finally:
        cursor.close()
        conn.close()

def get_all_users():
    """Get all users for admin management"""
    conn = get_db_connection()
    if not conn:
        return []
    
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT user_id, username, user_type, full_name FROM users ORDER BY created_at DESC")
        users = cursor.fetchall()
        return users
    except Exception as e:
        return []
    finally:
        cursor.close()
        conn.close()

def get_user_reports(user_id,hospital_id):
    """Get reports accessible to user"""
    conn = get_db_connection()
    if not conn:
        return []
    hospital_id = st.session_state.user['hospital_id']
    cursor = conn.cursor(dictionary=True)
    try:
        # Check user type
        cursor.execute("SELECT user_type FROM users WHERE user_id = %s", (user_id,))
        user_type_result = cursor.fetchone()
        user_type = user_type_result['user_type'] if user_type_result else 'user'
        
        if user_type == 'admin':
            # Admin sees all published reports
            cursor.execute("""
                SELECT r.*, p.first_name, p.last_name 
                FROM dexa_reports r 
                JOIN patients p ON r.patient_id = p.patient_id 
                WHERE r.is_published = TRUE AND r.hospital_id=%s
                ORDER BY r.created_at DESC
            """,(hospital_id,))
        else:
            # Regular users see only their linked reports
            cursor.execute("""
                SELECT r.*, p.first_name, p.last_name 
                FROM dexa_reports r 
                JOIN patients p ON r.patient_id = p.patient_id 
                JOIN patient_user_mapping m ON r.patient_id = m.patient_id 
                WHERE m.user_id = %s AND r.is_published = TRUE AND r.hospital_id = %s
                ORDER BY r.created_at DESC
            """, (user_id, hospital_id))
        
        
        reports = cursor.fetchall()
        return reports
    except Exception as e:
        return []
    finally:
        cursor.close()
        conn.close()

def get_hospital_users(hospital_id):
    """Get all users for a specific hospital"""
    conn = get_db_connection()
    if not conn:
        return []
    hospital_id = st.session_state.user['hospital_id']
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT user_id, username, user_type, full_name, mobile_number 
            FROM users 
            WHERE hospital_id = %s 
            ORDER BY created_at DESC
        """, (hospital_id,))
        users = cursor.fetchall()
        return users
    except Exception as e:
        return []
    finally:
        cursor.close()
        conn.close()

def get_hospital_patients(hospital_id):
    """Get all patients for a specific hospital"""
    conn = get_db_connection()
    if not conn:
        return []
    hospital_id = st.session_state.user['hospital_id']
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT patient_id, first_name, last_name, age, gender 
            FROM patients 
            WHERE hospital_id = %s 
            ORDER BY created_at DESC
        """, (hospital_id,))
        patients = cursor.fetchall()
        return patients
    except Exception as e:
        return []
    finally:
        cursor.close()
        conn.close()

# =============================================================================
# REPORT VERSION CONTROL
# =============================================================================

def get_report_versions(report_id):
    """Get all versions of a report"""
    conn = get_db_connection()
    if not conn:
        return []
    
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT * FROM report_versions 
            WHERE report_id = %s 
            ORDER BY version_number DESC
        """, (report_id,))
        
        versions = cursor.fetchall()
        return versions
    except Exception as e:
        return []
    finally:
        cursor.close()
        conn.close()

def save_report_version(report_id, report_data, edited_by, edit_reason):
    """Save a new version of the report with improved error handling"""
    conn = get_db_connection()
    if not conn:
        st.error("❌ Database connection failed for version control")
        return False
    
    cursor = conn.cursor()
    try:
        # Set transaction timeout
        cursor.execute("SET SESSION innodb_lock_wait_timeout = 30")
        cursor.execute("SET SESSION wait_timeout = 30")
        
        # Get current max version number
        cursor.execute("SELECT MAX(version_number) as max_version FROM report_versions WHERE report_id = %s", (report_id,))
        result = cursor.fetchone()
        next_version = (result[0] or 0) + 1
        
        # Convert date objects and other non-serializable types to strings for JSON
        serializable_data = {}
        for key, value in report_data.items():
            if isinstance(value, (date, datetime)):
                serializable_data[key] = value.isoformat()
            elif hasattr(value, 'isoformat'):  # Handle other date-like objects
                serializable_data[key] = value.isoformat()
            elif hasattr(value, '__dict__'):  # Handle objects
                serializable_data[key] = str(value)
            else:
                serializable_data[key] = value
        
        # Save version with explicit transaction management
        conn.start_transaction()
        cursor.execute("""
            INSERT INTO report_versions (report_id, version_number, report_data, edited_by, edit_reason)
            VALUES (%s, %s, %s, %s, %s)
        """, (report_id, next_version, json.dumps(serializable_data), edited_by, edit_reason))
        
        conn.commit()
        st.success(f"✅ Version {next_version} saved successfully!")
        return True
        
    except mysql.connector.Error as e:
        if e.errno == 1205:  # Lock wait timeout
            st.warning("⚠️ Database is busy. Please try again in a moment.")
            conn.rollback()
            # Retry once
            try:
                time.sleep(2)
                conn.commit()  # Try to clear any locks
                return save_report_version(report_id, report_data, edited_by, edit_reason)
            except:
                return False
        else:
           
            conn.rollback()
            return False
    except Exception as e:
        
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def publish_report_func(report_id):
    """Mark report as published"""
    conn = get_db_connection()
    if not conn:
        return False
    
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE dexa_reports 
            SET is_published = TRUE, published_at = CURRENT_TIMESTAMP 
            WHERE report_id = %s
        """, (report_id,))
        
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error publishing report: {str(e)}")
        return False
    finally:
        cursor.close()
        conn.close()

def get_todays_reports():
    """Get reports created today for editing"""
    conn = get_db_connection()
    if not conn:
        return []
    hospital_id = st.session_state.user['hospital_id']
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT r.*, p.first_name, p.last_name 
            FROM dexa_reports r 
            JOIN patients p ON r.patient_id = p.patient_id 
            WHERE DATE(r.created_at) = CURDATE() AND r.hospital_id = %s
            ORDER BY r.created_at DESC
        """, (hospital_id,))
        
        reports = cursor.fetchall()
        return reports
    except Exception as e:
        return []
    finally:
        cursor.close()
        conn.close()

def get_supabase_files_by_report(report_id):
    """Get all Supabase files for a specific report"""
    conn = get_db_connection()
    if not conn:
        return []
    
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT * FROM supabase_files 
            WHERE report_id = %s 
            ORDER BY created_at DESC
        """, (report_id,))
        
        files = cursor.fetchall()
        return files
    except Exception as e:
        return []
    finally:
        cursor.close()
        conn.close()

# =============================================================================
# UPDATED DATABASE FUNCTIONS
# =============================================================================


def save_report_data(report_data):
    """Save complete report data to database with all new fields including images - FIXED"""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        if not conn:
            st.error("❌ Failed to connect to database")
            return False
            
        cursor = conn.cursor()
        conn.start_transaction()
        # Save patient with hospital association
        cursor.execute("""
            INSERT IGNORE INTO patients (patient_id, hospital_id, first_name, last_name, age, gender)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (report_data['patient_id'], report_data['hospital_id'], report_data['first_name'], 
              report_data['last_name'], report_data['age'], report_data['gender']))
        
        # Save main report with all new fields
        cursor.execute("""
            INSERT INTO dexa_reports (
                report_id, patient_id, hospital_id, report_date, height, total_mass, fat_mass, 
                lean_mass, bone_mass, body_fat_percentage, muscle_mass_almi, 
                bone_density_t_score, z_score, visceral_fat_area, ag_ratio, ffmi,
                fracture_risk, muscle_loss_risk, 
                right_arm_fat, right_arm_lean, right_arm_bmc,
                left_arm_fat, left_arm_lean, left_arm_bmc,
                right_leg_fat, right_leg_lean, right_leg_bmc,
                left_leg_fat, left_leg_lean, left_leg_bmc,
                trunk_fat, trunk_lean, trunk_bmc,
                created_by, is_published
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                     %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            report_data['report_id'], report_data['patient_id'], report_data['hospital_id'],
            report_data['report_date'], report_data['height'], report_data['total_mass'], 
            report_data['fat_mass'], report_data['lean_mass'],
            report_data['bone_mass'], report_data['body_fat_percentage'],
            report_data['muscle_mass_almi'], report_data['bone_density_t_score'],
            report_data['z_score'], report_data['visceral_fat_area'], report_data['ag_ratio'],
            report_data['ffmi'], report_data['fracture_risk'],
            report_data['muscle_loss_risk'],
            report_data.get('right_arm_fat', 0), report_data.get('right_arm_lean', 0), report_data.get('right_arm_bmc', 0),
            report_data.get('left_arm_fat', 0), report_data.get('left_arm_lean', 0), report_data.get('left_arm_bmc', 0),
            report_data.get('right_leg_fat', 0), report_data.get('right_leg_lean', 0), report_data.get('right_leg_bmc', 0),
            report_data.get('left_leg_fat', 0), report_data.get('left_leg_lean', 0), report_data.get('left_leg_bmc', 0),
            report_data.get('trunk_fat', 0), report_data.get('trunk_lean', 0), report_data.get('trunk_bmc', 0),
            report_data['created_by'], report_data['is_published']
        ))
        
        if 'images' in report_data and report_data['images']:
            dexa_system = WeasyPrintPDFGenerator()
            success = dexa_system._save_report_images(report_data['report_id'], report_data['images'])
            if not success:
                st.warning("⚠️ Some images failed to save to database")
        
        # Save AP-Spine measurements
        for measurement in report_data.get('ap_spine_measurements', []):
            cursor.execute("""
                INSERT INTO ap_spine_measurements (report_id, region, bmd, t_score, z_score)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                report_data['report_id'], measurement['region'], 
                measurement['bmd'], measurement['t_score'], measurement['z_score']
            ))
        
        # Save Femur measurements
        for measurement in report_data.get('femur_measurements', []):
            cursor.execute("""
                INSERT INTO femur_measurements (report_id, side, region, bmd, t_score, z_score)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                report_data['report_id'], measurement['side'], measurement['region'],
                measurement['bmd'], measurement['t_score'], measurement['z_score']
            ))
        
        conn.commit()
        
        # Save initial version
        version_saved = save_report_version(
            report_data['report_id'], 
            report_data, 
            report_data['created_by'], 
            "Initial version"
        )
        
        conn.commit()
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        if conn:
            conn.rollback()
        st.error(f"❌ General Error saving report: {str(e)}")
        return False

def prepare_report_data(db_report):
    """Prepare report data for PDF generation with all fields"""
    if isinstance(db_report, dict):
        # Get AP-Spine measurements
        ap_spine_measurements = []
        right_femur_measurements = []
        left_femur_measurements = []
        
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM ap_spine_measurements WHERE report_id = %s", (db_report['report_id'],))
            ap_spine_measurements = cursor.fetchall()
            
            # Get Femur measurements
            cursor.execute("SELECT * FROM femur_measurements WHERE report_id = %s", (db_report['report_id'],))
            femur_measurements = cursor.fetchall()
            
            # Separate right and left femur measurements
            for measurement in femur_measurements:
                if measurement['side'] == 'RIGHT':
                    right_femur_measurements.append(measurement)
                else:
                    left_femur_measurements.append(measurement)
            
            cursor.close()
            conn.close()
        
        return {
            'patient_id': db_report['patient_id'],
            'report_id': db_report['report_id'],
            'patient_name': f"{db_report['first_name']} {db_report['last_name']}",
            'age': db_report.get('age', 36),
            'gender': db_report.get('gender', 'M'),
            'report_date': db_report['report_date'].strftime('%d %b %Y') if hasattr(db_report['report_date'], 'strftime') else db_report['report_date'],
            'height': db_report.get('height', 171),
            'total_mass': db_report['total_mass'],
            'fat_mass': db_report['fat_mass'],
            'lean_mass': db_report['lean_mass'],
            'bone_mass': db_report['bone_mass'],
            'body_fat_percentage': db_report['body_fat_percentage'],
            'muscle_mass_almi': db_report['muscle_mass_almi'],
            'bone_density_t_score': db_report['bone_density_t_score'],
            'visceral_fat_area': db_report['visceral_fat_area'],
            'ag_ratio': db_report['ag_ratio'],
            'ffmi': db_report['ffmi'],
            'fracture_risk': db_report['fracture_risk'],
            'muscle_loss_risk': db_report['muscle_loss_risk'],
            'z_score': db_report.get('z_score', -0.6),
            
            # Regional composition
            'right_arm_fat': db_report.get('right_arm_fat', 3.2),
            'right_arm_lean': db_report.get('right_arm_lean', 2.8),
            'right_arm_bmc': db_report.get('right_arm_bmc', 0.15),
            'left_arm_fat': db_report.get('left_arm_fat', 3.1),
            'left_arm_lean': db_report.get('left_arm_lean', 2.7),
            'left_arm_bmc': db_report.get('left_arm_bmc', 0.14),
            'right_leg_fat': db_report.get('right_leg_fat', 8.5),
            'right_leg_lean': db_report.get('right_leg_lean', 7.2),
            'right_leg_bmc': db_report.get('right_leg_bmc', 0.45),
            'left_leg_fat': db_report.get('left_leg_fat', 8.3),
            'left_leg_lean': db_report.get('left_leg_lean', 7.1),
            'left_leg_bmc': db_report.get('left_leg_bmc', 0.44),
            'trunk_fat': db_report.get('trunk_fat', 18.5),
            'trunk_lean': db_report.get('trunk_lean', 25.8),
            'trunk_bmc': db_report.get('trunk_bmc', 0.85),
            
            # Measurements
            'ap_spine_measurements': ap_spine_measurements,
            'right_femur_measurements': right_femur_measurements,
            'left_femur_measurements': left_femur_measurements
        }

def update_existing_report(report_data):
    """Update an existing report in the database with better transaction handling"""
    conn = get_db_connection()
    if not conn:
        return False
        
    cursor = conn.cursor()
    try:
        # Set timeouts
        cursor.execute("SET SESSION innodb_lock_wait_timeout = 30")
        cursor.execute("SET SESSION wait_timeout = 30")
        
        # Start transaction
        conn.start_transaction()
        
        # Update main report
        cursor.execute("""
            UPDATE dexa_reports SET
                patient_id = %s,
                report_date = %s,
                height = %s,
                total_mass = %s,
                fat_mass = %s,
                lean_mass = %s,
                bone_mass = %s,
                body_fat_percentage = %s,
                muscle_mass_almi = %s,
                bone_density_t_score = %s,
                z_score = %s,
                visceral_fat_area = %s,
                ag_ratio = %s,
                ffmi = %s,
                fracture_risk = %s,
                muscle_loss_risk = %s,
                right_arm_fat = %s,
                right_arm_lean = %s,
                right_arm_bmc = %s,
                left_arm_fat = %s,
                left_arm_lean = %s,
                left_arm_bmc = %s,
                right_leg_fat = %s,
                right_leg_lean = %s,
                right_leg_bmc = %s,
                left_leg_fat = %s,
                left_leg_lean = %s,
                left_leg_bmc = %s,
                trunk_fat = %s,
                trunk_lean = %s,
                trunk_bmc = %s,
                is_published = %s,
                last_edited = CURRENT_TIMESTAMP,
                edit_count = edit_count + 1
            WHERE report_id = %s
        """, (
            report_data['patient_id'], report_data['report_date'], report_data['height'],
            report_data['total_mass'], report_data['fat_mass'], report_data['lean_mass'],
            report_data['bone_mass'], report_data['body_fat_percentage'], report_data['muscle_mass_almi'],
            report_data['bone_density_t_score'], report_data['z_score'], report_data['visceral_fat_area'],
            report_data['ag_ratio'], report_data['ffmi'], report_data['fracture_risk'],
            report_data['muscle_loss_risk'], report_data['right_arm_fat'], report_data['right_arm_lean'],
            report_data['right_arm_bmc'], report_data['left_arm_fat'], report_data['left_arm_lean'],
            report_data['left_arm_bmc'], report_data['right_leg_fat'], report_data['right_leg_lean'],
            report_data['right_leg_bmc'], report_data['left_leg_fat'], report_data['left_leg_lean'],
            report_data['left_leg_bmc'], report_data['trunk_fat'], report_data['trunk_lean'],
            report_data['trunk_bmc'], report_data['is_published'], report_data['report_id']
        ))
        
        conn.commit()
        return True
        
    except mysql.connector.Error as e:
        if e.errno == 1205:  # Lock wait timeout
            conn.rollback()
            return False
        else:
            conn.rollback()
            return False
    except Exception as e:
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

# =============================================================================
# STREAMLIT UI COMPONENTS - UPDATED WITH EYE ICON PREVIEWS
# =============================================================================

def show_image_preview_page(image_data, title):
    """Show a full page preview for an image"""
    st.markdown(f"<h1 style='text-align: center;'>🔍 {title}</h1>", unsafe_allow_html=True)
    
    if image_data:
        try:
            # Display the image
            st.image(image_data, use_column_width=True)
            
            # Download button
            st.download_button(
                label="📥 Download Image",
                data=image_data.getvalue(),
                file_name=f"{title.replace(' ', '_')}.jpg",
                mime="image/jpeg"
            )
        except Exception as e:
            st.error(f"Error displaying image: {str(e)}")
    else:
        st.warning("No image data available")
    
    # Back button
    if st.button("← Back"):
        st.session_state.show_image_preview = False
        st.rerun()

def show_pdf_preview_page(pdf_bytes, title):
    """Show a full page preview for a PDF"""
    st.markdown(f"<h1 style='text-align: center;'>📄 {title}</h1>", unsafe_allow_html=True)
    
    if pdf_bytes:
        try:
            # Display PDF
            base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
            pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf"></iframe>'
            st.markdown(pdf_display, unsafe_allow_html=True)
            
            # Download button
            st.download_button(
                label="📥 Download PDF",
                data=pdf_bytes,
                file_name=f"{title.replace(' ', '_')}.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"Error displaying PDF: {str(e)}")
    else:
        st.warning("No PDF data available")
    
    # Back button
    if st.button("← Back"):
        st.session_state.show_pdf_preview = False
        st.rerun()

def create_eye_icon_button(label, key, help_text="Click to preview"):
    """Create a clickable eye icon button"""
    return st.button(
        f"👁️ {label}", 
        key=key,
        help=help_text,
        use_container_width=True
    )

def show_pdf_generation_options():
    """Show PDF generation options"""
    st.markdown("### 📄 PDF Generation Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        use_exact_pdf = st.checkbox(
            "Use WeasyPrint HTML Replication", 
            value=True,
            help="Generate pixel-perfect PDF matching the HTML design using WeasyPrint."
        )
    
    with col2:
        page_size = st.selectbox(
            "Page Size",
            ["A4", "A5"],
            index=0
        )
    
    return use_exact_pdf, page_size
def create_new_report(dexa_system):
    """Create new DEXA report with all detailed fields matching the exact template"""
    st.markdown('<div class="section-header">📝 Create New DEXA Report</div>', unsafe_allow_html=True)
    if 'generated_pdfs' not in st.session_state:
        st.session_state.generated_pdfs = {}
    
    # PDF Generation Options
    use_exact_pdf, page_size = show_pdf_generation_options()
    
    # Initialize form data
    form_data = {}
    
    with st.form("dexa_report_form", clear_on_submit=True):
        st.markdown('<div class="section-header">👤 Patient Information</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        
        with col1:
            patient_id = st.text_input("🆔 Patient ID*", value="000480")
            first_name = st.text_input("👤 First Name*", value="BRI")
            last_name = st.text_input("👤 Last Name*", value="K")
            age = st.number_input("🎂 Age*", min_value=1, max_value=120, value=36)
            gender = st.selectbox("⚧ Gender*", ["M", "F"], index=0)
        
        with col2:
            report_id = st.text_input("📋 Report ID*", value="000653")
            report_date = st.date_input("📅 Report Date*", value=date.today())
            height = st.number_input("📏 Height (cm)*", min_value=100, max_value=250, value=171)
        
        st.markdown('<div class="section-header">⚖️ Body Composition</div>', unsafe_allow_html=True)
        col3, col4 = st.columns(2)
        
        with col3:
            total_mass = st.number_input("⚖️ Total Mass (kg)*", min_value=0.0, value=104.6)
            fat_mass = st.number_input("🩸 Fat Mass (kg)*", min_value=0.0, value=39.79)
            lean_mass = st.number_input("💪 Lean Mass (kg)*", min_value=0.0, value=61.84)
            bone_mass = st.number_input("🦴 Bone Mass (kg)*", min_value=0.0, value=2.94)
        
        with col4:
            body_fat_percentage = st.number_input("📊 Body Fat Percentage*", min_value=0.0, max_value=100.0, value=38.0)
            muscle_mass_almi = st.number_input("🏋️ Muscle Mass ALMI (kg/m²)*", min_value=0.0, value=10.23)
            bone_density_t_score = st.number_input("🦴 Bone Density T-Score*", value=-0.6)
            z_score = st.number_input("📈 Z-Score*", value=-0.6)
        
        st.markdown('<div class="section-header">📈 Additional Metrics</div>', unsafe_allow_html=True)
        col5, col6 = st.columns(2)
        
        with col5:
            visceral_fat_area = st.number_input("🎯 Visceral Fat Area (cm²)*", min_value=0.0, value=170.0)
            ag_ratio = st.number_input("📐 A/G Ratio*", min_value=0.0, value=1.23)
            ffmi = st.number_input("💪 FFMI (kg/m²)*", min_value=0.0, value=20.67)
        
        with col6:
            fracture_risk = st.selectbox("⚠️ Fracture Risk*", ["LOW", "MODERATE", "HIGH"], index=0)
            muscle_loss_risk = st.selectbox("💪 Muscle Loss Risk*", ["LOW", "MODERATE", "HIGH"], index=0)
        
        # Regional Composition Data - ARMS
        st.markdown('<div class="section-header">💪 Arms Composition</div>', unsafe_allow_html=True)
        
        st.subheader("Right Arm")
        col7, col8, col9 = st.columns(3)
        with col7:
            right_arm_fat = st.number_input("Right Arm Fat (kg)", min_value=0.0, value=3.2, key="right_arm_fat")
        with col8:
            right_arm_lean = st.number_input("Right Arm Lean (kg)", min_value=0.0, value=2.8, key="right_arm_lean")
        with col9:
            right_arm_bmc = st.number_input("Right Arm BMC (kg)", min_value=0.0, value=0.15, key="right_arm_bmc")
        
        st.subheader("Left Arm")
        col10, col11, col12 = st.columns(3)
        with col10:
            left_arm_fat = st.number_input("Left Arm Fat (kg)", min_value=0.0, value=3.1, key="left_arm_fat")
        with col11:
            left_arm_lean = st.number_input("Left Arm Lean (kg)", min_value=0.0, value=2.7, key="left_arm_lean")
        with col12:
            left_arm_bmc = st.number_input("Left Arm BMC (kg)", min_value=0.0, value=0.14, key="left_arm_bmc")
        
        # Regional Composition Data - LEGS
        st.markdown('<div class="section-header">🦵 Legs Composition</div>', unsafe_allow_html=True)
        
        st.subheader("Right Leg")
        col13, col14, col15 = st.columns(3)
        with col13:
            right_leg_fat = st.number_input("Right Leg Fat (kg)", min_value=0.0, value=8.5, key="right_leg_fat")
        with col14:
            right_leg_lean = st.number_input("Right Leg Lean (kg)", min_value=0.0, value=7.2, key="right_leg_lean")
        with col15:
            right_leg_bmc = st.number_input("Right Leg BMC (kg)", min_value=0.0, value=0.45, key="right_leg_bmc")
        
        st.subheader("Left Leg")
        col16, col17, col18 = st.columns(3)
        with col16:
            left_leg_fat = st.number_input("Left Leg Fat (kg)", min_value=0.0, value=8.3, key="left_leg_fat")
        with col17:
            left_leg_lean = st.number_input("Left Leg Lean (kg)", min_value=0.0, value=7.1, key="left_leg_lean")
        with col18:
            left_leg_bmc = st.number_input("Left Leg BMC (kg)", min_value=0.0, value=0.44, key="left_leg_bmc")
        
        # Regional Composition Data - TRUNK
        st.markdown('<div class="section-header">🦺 Trunk Composition</div>', unsafe_allow_html=True)
        
        col19, col20, col21 = st.columns(3)
        with col19:
            trunk_fat = st.number_input("Trunk Fat (kg)", min_value=0.0, value=18.5, key="trunk_fat")
        with col20:
            trunk_lean = st.number_input("Trunk Lean (kg)", min_value=0.0, value=25.8, key="trunk_lean")
        with col21:
            trunk_bmc = st.number_input("Trunk BMC (kg)", min_value=0.0, value=0.85, key="trunk_bmc")
        
        # Medical Images Upload Section
        st.markdown('<div class="section-header">🖼️ Medical Images</div>', unsafe_allow_html=True)
        
        col_img1, col_img2 = st.columns(2)
        
        with col_img1:
            st.subheader("AP-Spine Image")
            ap_spine_image = st.file_uploader("Upload AP-Spine Image", type=['png', 'jpg', 'jpeg'], key="ap_spine")
            
            st.subheader("Right Femur Image")
            right_femur_image = st.file_uploader("Upload Right Femur Image", type=['png', 'jpg', 'jpeg'], key="right_femur")
            
            st.subheader("Full Body Image")
            full_body_image = st.file_uploader("Upload Full Body Image", type=['png', 'jpg', 'jpeg'], key="full_body")
        
        with col_img2:
            st.subheader("Left Femur Image")
            left_femur_image = st.file_uploader("Upload Left Femur Image", type=['png', 'jpg', 'jpeg'], key="left_femur")
            
            st.subheader("Fat Distribution Image")
            fat_distribution_image = st.file_uploader("Upload Fat Distribution Image", type=['png', 'jpg', 'jpeg'], key="fat_dist")
        
        # AP-Spine Measurements
        st.markdown('<div class="section-header">📊 AP-Spine Measurements</div>', unsafe_allow_html=True)
        
        ap_spine_measurements = []
        spine_regions = ['L1', 'L2', 'L3', 'L4', 'L1-L4']
        
        for region in spine_regions:
            st.subheader(f"AP-Spine {region}")
            col_sp1, col_sp2, col_sp3 = st.columns(3)
            with col_sp1:
                bmd = st.number_input(f"BMD {region} (g/cm²)", min_value=0.0, value=1.2, key=f"spine_bmd_{region}")
            with col_sp2:
                t_score = st.number_input(f"T-Score {region}", value=-0.6, key=f"spine_t_{region}")
            with col_sp3:
                z_score = st.number_input(f"Z-Score {region}", value=0.3, key=f"spine_z_{region}")
            
            ap_spine_measurements.append({
                'region': region,
                'bmd': bmd,
                't_score': t_score,
                'z_score': z_score
            })
        
        # Femur Measurements
        st.markdown('<div class="section-header">📊 Femur Measurements</div>', unsafe_allow_html=True)
        
        femur_measurements = []
        femur_regions = ['NECK', 'TOTAL']
        
        st.subheader("Right Femur")
        for region in femur_regions:
            col_fm1, col_fm2, col_fm3 = st.columns(3)
            with col_fm1:
                bmd = st.number_input(f"BMD Right {region} (g/cm²)", min_value=0.0, value=1.0, key=f"rfemur_bmd_{region}")
            with col_fm2:
                t_score = st.number_input(f"T-Score Right {region}", value=-0.6, key=f"rfemur_t_{region}")
            with col_fm3:
                z_score = st.number_input(f"Z-Score Right {region}", value=-0.6, key=f"rfemur_z_{region}")
            
            femur_measurements.append({
                'side': 'RIGHT',
                'region': region,
                'bmd': bmd,
                't_score': t_score,
                'z_score': z_score
            })
        
        st.subheader("Left Femur")
        for region in femur_regions:
            col_fm4, col_fm5, col_fm6 = st.columns(3)
            with col_fm4:
                bmd = st.number_input(f"BMD Left {region} (g/cm²)", min_value=0.0, value=1.0, key=f"lfemur_bmd_{region}")
            with col_fm5:
                t_score = st.number_input(f"T-Score Left {region}", value=0.1, key=f"lfemur_t_{region}")
            with col_fm6:
                z_score = st.number_input(f"Z-Score Left {region}", value=0.0, key=f"lfemur_z_{region}")
            
            femur_measurements.append({
                'side': 'LEFT',
                'region': region,
                'bmd': bmd,
                't_score': t_score,
                'z_score': z_score
            })
        
        # User assignment
        users = get_all_users()
        user_options = {f"{u['full_name']} ({u['username']})": u['user_id'] for u in users if u['user_type'] == 'user'}
        if user_options:
            selected_user = st.selectbox("Assign to User", list(user_options.keys()))
            assign_to_user = user_options[selected_user]
        else:
            assign_to_user = None
        
        # Submit buttons
        st.markdown("---")
        col20, col21 = st.columns(2)
        with col20:
            save_draft = st.form_submit_button("💾 Save as Draft", use_container_width=True)
        with col21:
            publish_report = st.form_submit_button("🚀 Publish Report", use_container_width=True)
    
    # Handle form submission OUTSIDE the form
    if save_draft or publish_report:
        # Validate required fields
        required_fields = {
            "Patient ID": patient_id,
            "Report ID": report_id,
            "First Name": first_name,
            "Last Name": last_name,
            "Height": height
        }
        
        missing_fields = [field for field, value in required_fields.items() if not value]
        if missing_fields:
            st.error(f"❌ Please fill in: {', '.join(missing_fields)}")
        else:
            # Check if report ID already exists
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("SELECT report_id FROM dexa_reports WHERE report_id = %s", (report_id,))
                existing_report = cursor.fetchone()
                cursor.close()
                conn.close()
                
                if existing_report:
                    st.error(f"❌ Report ID {report_id} already exists.")
                else:
                    # Prepare image data
                    image_data = {
                        'ap_spine': ap_spine_image,
                        'right_femur': right_femur_image,
                        'left_femur': left_femur_image,
                        'full_body': full_body_image,
                        'fat_distribution': fat_distribution_image
                    }
                    
                    # Save report data
                    report_data = {
                        'patient_id': patient_id,
                        'report_id': report_id,
                        'first_name': first_name,
                        'last_name': last_name,
                        'age': age,
                        'gender': gender,
                        'height': height,
                        'report_date': report_date,
                        'total_mass': total_mass,
                        'fat_mass': fat_mass,
                        'lean_mass': lean_mass,
                        'bone_mass': bone_mass,
                        'body_fat_percentage': body_fat_percentage,
                        'muscle_mass_almi': muscle_mass_almi,
                        'bone_density_t_score': bone_density_t_score,
                        'z_score': z_score,
                        'visceral_fat_area': visceral_fat_area,
                        'ag_ratio': ag_ratio,
                        'ffmi': ffmi,
                        'fracture_risk': fracture_risk,
                        'muscle_loss_risk': muscle_loss_risk,
                        
                        # Regional composition fields
                        'right_arm_fat': right_arm_fat,
                        'right_arm_lean': right_arm_lean,
                        'right_arm_bmc': right_arm_bmc,
                        'left_arm_fat': left_arm_fat,
                        'left_arm_lean': left_arm_lean,
                        'left_arm_bmc': left_arm_bmc,
                        'right_leg_fat': right_leg_fat,
                        'right_leg_lean': right_leg_lean,
                        'right_leg_bmc': right_leg_bmc,
                        'left_leg_fat': left_leg_fat,
                        'left_leg_lean': left_leg_lean,
                        'left_leg_bmc': left_leg_bmc,
                        'trunk_fat': trunk_fat,
                        'trunk_lean': trunk_lean,
                        'trunk_bmc': trunk_bmc,
                        
                        # Image data
                        'images': image_data,
                        
                        
                        # Measurement data
                        'ap_spine_measurements': ap_spine_measurements,
                        'femur_measurements': femur_measurements,
                        
                        'hospital_id': st.session_state.user['hospital_id'],
                        'created_by': st.session_state.user['user_id'],
                        'is_published': bool(publish_report)
                    }
                    
                    if save_report_data(report_data):
                        if publish_report:
                            # Mark as published
                            publish_report_func(report_id)
                            
                            # Generate PDFs and store them in session state for download outside the form
                            pdf_report_data = prepare_report_data(report_data)
                            
                            # Generate PDF with selected options
                            pdf_bytes = dexa_system.generate_pdf(pdf_report_data, page_size)
                            if pdf_bytes:
                                success = dexa_system.save_to_supabase_storage(
                                    pdf_bytes, 
                                    f"{report_data['report_id']}_{page_size}.pdf",
                                    report_data['report_id'],
                                    page_size
                                )
                                if success:
                                    st.session_state.generated_pdfs[f"{page_size.lower()}_{report_id}"] = pdf_bytes
                                    st.success(f"✅ PDF generated and stored! Report ID: {report_id}")
                                else:
                                    st.error("❌ PDF generated but failed to save to cloud storage")
                            else:
                                st.error("❌ Failed to generate PDF")
                            
                            st.success("✅ Report published successfully!")
                        else:
                            st.success("✅ Report saved as draft!")
                        
                        # Link to user if specified
                        if assign_to_user:
                            link_patient_to_user(patient_id, assign_to_user)
                            st.success("✅ Report linked to user!")
                        
                        if publish_report:
                            st.balloons()
                    else:
                        st.error("❌ Failed to save report data to database")
    
    # Handle image previews AFTER form submission (outside the form)
    if any([ap_spine_image, right_femur_image, left_femur_image, full_body_image, fat_distribution_image]):
        st.markdown("---")
        st.subheader("🖼️ Image Previews")
        
        preview_images = [
            ("AP-Spine", ap_spine_image),
            ("Right Femur", right_femur_image),
            ("Left Femur", left_femur_image),
            ("Full Body", full_body_image),
            ("Fat Distribution", fat_distribution_image)
        ]
        
        for name, img in preview_images:
            if img is not None:
                col_preview1, col_preview2 = st.columns([3, 1])
                with col_preview1:
                    st.write(f"**{name}** - {img.size // 1024} KB")
                with col_preview2:
                    if st.button(f"👁️ Preview {name}", key=f"preview_{name}"):
                        st.session_state.show_image_preview = True
                        st.session_state.preview_image_data = img
                        st.session_state.preview_image_title = name
                        st.rerun()

# =============================================================================
# MAIN APPLICATION
# =============================================================================
def main():
    # Custom CSS for colorful UI
    st.markdown("""
        <style>
        .main-header {
            font-size: 3rem;
            font-weight: bold;
            background: linear-gradient(45deg, #FF6B6B, #4ECDC4, #45B7D1, #96CEB4);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
            margin-bottom: 2rem;
        }
        .hospital-info {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1.5rem;
            border-radius: 1rem;
            color: white;
            margin: 0.5rem 0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .section-header {
            font-size: 1.8rem;
            font-weight: bold;
            color: #2E86AB;
            border-left: 5px solid #2E86AB;
            padding-left: 1rem;
            margin: 2rem 0 1rem 0;
            background: linear-gradient(90deg, #F8F9FA, #FFFFFF);
            padding: 1rem;
            border-radius: 0.5rem;
        }
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1.5rem;
            border-radius: 1rem;
            color: white;
            margin: 0.5rem 0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .metric-value {
            font-size: 2rem;
            font-weight: bold;
            margin: 0.5rem 0;
        }
        .metric-label {
            font-size: 0.9rem;
            opacity: 0.9;
        }
        .success-box {
            background: linear-gradient(135deg, #56ab2f 0%, #a8e6cf 100%);
            padding: 1.5rem;
            border-radius: 1rem;
            color: white;
            margin: 1rem 0;
            border-left: 5px solid #2E8B57;
        }
        .warning-box {
            background: linear-gradient(135deg, #f7971e 0%, #ffd200 100%);
            padding: 1.5rem;
            border-radius: 1rem;
            color: white;
            margin: 1rem 0;
            border-left: 5px solid #FF8C00;
        }
        .danger-box {
            background: linear-gradient(135deg, #ff6b6b 0%, #ff8e8e 100%);
            padding: 1.5rem;
            border-radius: 1rem;
            color: white;
            margin: 1rem 0;
            border-left: 5px solid #DC143C;
        }
        .info-box {
            background: linear-gradient(135deg, #4ECDC4 0%, #44A08D 100%);
            padding: 1.5rem;
            border-radius: 1rem;
            color: white;
            margin: 1rem 0;
            border-left: 5px solid #008B8B;
        }
        .error-box {
            background: linear-gradient(135deg, #ff6b6b 0%, #ff8e8e 100%);
            padding: 1.5rem;
            border-radius: 1rem;
            color: white;
            margin: 1rem 0;
            border-left: 5px solid #DC143C;
        }
        .stButton>button {
            background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
            color: white;
            border: none;
            padding: 0.5rem 2rem;
            border-radius: 0.5rem;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        .eye-button {
            background: linear-gradient(45deg, #FFA726, #FF9800) !important;
        }
        </style>
    """, unsafe_allow_html=True)

    st.set_page_config(
        page_title="Hospital DEXA Report System",
        page_icon="🏥",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize database
    init_database()
    
    # Update database schema to add missing columns
    update_database_schema()
    
    # Initialize system with WeasyPrint PDF Generator
    dexa_system = WeasyPrintPDFGenerator()
    
    # Initialize session state
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'show_register' not in st.session_state:
        st.session_state.show_register = False
    if 'show_hospital_registration' not in st.session_state:
        st.session_state.show_hospital_registration = False
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "🏠 Dashboard"
    if 'editing_report' not in st.session_state:
        st.session_state.editing_report = None
    if 'edit_report_data' not in st.session_state:
        st.session_state.edit_report_data = None
    if 'generated_pdfs' not in st.session_state:
        st.session_state.generated_pdfs = {}
    if 'show_help_section' not in st.session_state:
        st.session_state.show_help_section = False
    
    # NEW: Preview session states
    if 'show_image_preview' not in st.session_state:
        st.session_state.show_image_preview = False
    if 'show_pdf_preview' not in st.session_state:
        st.session_state.show_pdf_preview = False
    if 'preview_image_data' not in st.session_state:
        st.session_state.preview_image_data = None
    if 'preview_image_title' not in st.session_state:
        st.session_state.preview_image_title = ""
    if 'preview_pdf_data' not in st.session_state:
        st.session_state.preview_pdf_data = None
    if 'preview_pdf_title' not in st.session_state:
        st.session_state.preview_pdf_title = ""
    
    # Check authentication
    if not st.session_state.user:
        if st.session_state.show_hospital_registration:
            show_hospital_registration_page()
        elif st.session_state.show_register:
            show_user_registration_page()
        else:
            show_login_page()
        return
    
    # Handle preview pages first
    if st.session_state.show_image_preview:
        show_image_preview_page(st.session_state.preview_image_data, st.session_state.preview_image_title)
        return
        
    if st.session_state.show_pdf_preview:
        show_pdf_preview_page(st.session_state.preview_pdf_data, st.session_state.preview_pdf_title)
        return
    
    # User is authenticated - show main application
    user = st.session_state.user
    # Show hospital header
    show_hospital_header(user)
    
    # Different interfaces for admin vs regular users
    if user['user_type'] == 'admin':
        show_admin_interface(dexa_system, user)
    else:
        show_user_interface(dexa_system, user)

def show_hospital_header(user):
    """Show hospital information header"""
    st.markdown(f'<div class="main-header">🏥 {user["hospital_name"]}</div>', unsafe_allow_html=True)
    
    # Show hospital contact information
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div class="hospital-info">📍 {user["address"]}</div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="hospital-info">📞 {user["phone_number"]}</div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="hospital-info">✉️ {user["email"]}</div>', unsafe_allow_html=True)
    
    # User info and logout
    col4, col5 = st.columns([3, 1])
    with col4:
        st.write(f"Welcome, **{user['full_name']}** ({user['user_type'].title()})")
    with col5:
        if st.button("🚪 Logout"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

def show_admin_interface(dexa_system, user):
    """Admin interface with sidebar navigation"""
    with st.sidebar:
        st.markdown("### 📊 Navigation")
        menu_options = ["🏠 Dashboard", "📝 Data Management", "👥 User Management", "📋 Reports", "💾 Storage"]
        selected_page = st.selectbox("Choose Section", menu_options, key="admin_nav")
        
        if selected_page != st.session_state.current_page:
            st.session_state.current_page = selected_page
            st.rerun()
    
    # Route to appropriate section
    if st.session_state.current_page == "🏠 Dashboard":
        show_admin_dashboard(dexa_system, user)
    elif st.session_state.current_page == "📝 Data Management":
        show_admin_data_management(dexa_system, user)
    elif st.session_state.current_page == "👥 User Management":
        show_admin_user_management(user)
    elif st.session_state.current_page == "📋 Reports":
        show_admin_reports(dexa_system, user)
    elif st.session_state.current_page == "💾 Storage":
        show_cloud_storage(dexa_system)

def show_user_interface(dexa_system, user):
    """User interface - single page for regular users"""
    show_user_reports_page(dexa_system, user)

def show_admin_dashboard(dexa_system, user):
    """Enhanced system dashboard with recent reports"""
    st.markdown('<div class="section-header">📊 System Dashboard</div>', unsafe_allow_html=True)
    
    # Get database stats
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT COUNT(*) as count FROM patients")
        total_patients = cursor.fetchone()
        
        cursor.execute("SELECT COUNT(*) as count FROM dexa_reports")
        total_reports = cursor.fetchone()
        
        cursor.execute("SELECT COUNT(*) as count FROM dexa_reports WHERE report_date = %s", (date.today(),))
        today_reports = cursor.fetchone()
        
        cursor.close()
        conn.close()
    else:
        total_patients = {'count': 0}
        total_reports = {'count': 0}
        today_reports = {'count': 0}
    
    # Get user-specific reports
    user_reports = get_user_reports(st.session_state.user['user_id'], st.session_state.user['hospital_id'])
    
    # Get Supabase storage info
    file_count, total_size_mb = dexa_system.get_storage_info()
    
    # Display metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Total Patients</div>
                <div class="metric-value">{total_patients['count']}</div>
                <div>👥 Registered</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Total Reports</div>
                <div class="metric-value">{total_reports['count']}</div>
                <div>📋 Generated</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Today's Reports</div>
                <div class="metric-value">{today_reports['count']}</div>
                <div>📅 Today</div>
            </div>
        """, unsafe_allow_html=True)
    
    col4, col5, col6 = st.columns(3)
    
    with col4:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">My Reports</div>
                <div class="metric-value">{len(user_reports)}</div>
                <div>📄 Accessible</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Cloud PDFs</div>
                <div class="metric-value">{file_count}</div>
                <div>☁️ Stored</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col6:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Storage Used</div>
                <div class="metric-value">{total_size_mb:.1f} MB</div>
                <div>📦 Cloud</div>
            </div>
        """, unsafe_allow_html=True)
    
    # Recent Reports Section - FIXED: Use stored files instead of regular reports
    st.markdown('<div class="section-header">📋 Recent Stored PDFs</div>', unsafe_allow_html=True)
    
    # Get stored files from Supabase
    stored_files = dexa_system.list_stored_reports()
    recent_files = stored_files[:5] if stored_files else []
    
    if recent_files:
        for i, file in enumerate(recent_files):
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            
            with col1:
                # FIX: Use file data instead of report data
                st.markdown(f"""
                    <div class="info-box">
                        <strong>{file['filename']}</strong><br>
                        <small>Report: {file.get('first_name', 'N/A')} {file.get('last_name', 'N/A')} ({file['report_id']})</small><br>
                        <small>Size: {file['file_size_kb']} KB | Format: {file['file_format']} | Uploaded: {file['created_at'].strftime('%Y-%m-%d %H:%M')}</small><br>
                        <small>URL: <a href="{file['file_url']}" target="_blank">View File</a></small>
                    </div>
                """, unsafe_allow_html=True)
            
            with col2:
                # Download from URL
                st.download_button(
                    label="📥 Download",
                    data=requests.get(file['file_url']).content,
                    file_name=file['filename'],
                    mime="application/pdf",
                    key=f"download_{file['unique_filename']}_{i}",
                    use_container_width=True
                )
            
            with col3:
                # Preview with eye icon
                if create_eye_icon_button("Preview", f"cloud_storage_preview_{file['unique_filename']}_{i}"):
                    st.session_state.show_pdf_preview = True
                    st.session_state.preview_pdf_data = requests.get(file['file_url']).content
                    st.session_state.preview_pdf_title = f"Cloud Storage: {file['filename']}"
                    st.rerun()
            
            with col4:
                st.write(f"🔗 [Link]({file['file_url']})")
        
        if len(stored_files) > 5:
            st.info(f"📚 Showing 5 most recent PDFs out of {len(stored_files)} total stored files.")
    else:
        st.markdown("""
            <div class="warning-box">
                No PDF reports stored yet.
            </div>
        """, unsafe_allow_html=True)
def show_admin_data_management(dexa_system, user=None):
    """Admin data management interface - EXCLUSIVE data entry point"""
    st.markdown('<div class="section-header">📊 Admin Data Management</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["➕ Create New Report", "📋 Manage Reports", "🔄 Version History"])
    
    with tab1:
        create_new_report(dexa_system)
    
    with tab2:
        manage_reports(dexa_system)
    
    with tab3:
        show_version_history()

def manage_reports(dexa_system):
    """Manage existing reports with editing capabilities"""
    st.markdown('<div class="section-header">📋 Manage Reports</div>', unsafe_allow_html=True)
    
    # Check if we're in edit mode for a specific report
    if st.session_state.editing_report:
        show_edit_report_form(dexa_system, st.session_state.editing_report, st.session_state.edit_report_data)
        return
    
    # Show today's reports for editing with clear restriction notice
    st.subheader("📝 Today's Reports (Editable - Same Day Only)")
    
    # Add explicit restriction notice
    st.info("🔒 **Editing Policy**: Reports can only be edited on the same day they were created. Published reports become read-only after the creation day.")
    
    todays_reports = get_todays_reports()
    
    if todays_reports:
        for i, report in enumerate(todays_reports):
            with st.expander(f"📄 {report['first_name']} {report['last_name']} - {report['report_id']} ({'Published' if report['is_published'] else 'Draft'})"):
                display_report_summary(report)
                
                # Show creation date clearly
                created_date = report['created_at'].date() if hasattr(report['created_at'], 'date') else report['created_at']
                st.caption(f"📅 Created: {created_date}")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button(f"✏️ Edit Report", key=f"edit_{report['report_id']}_{i}"):
                        st.session_state.editing_report = report['report_id']
                        st.session_state.edit_report_data = report
                        st.rerun()
                
                with col2:
                    if not report['is_published']:
                        if st.button(f"🚀 Publish", key=f"publish_{report['report_id']}_{i}"):
                            if publish_report_func(report['report_id']):
                                st.markdown('<div class="success-box">✅ Report published!</div>', unsafe_allow_html=True)
                                # Generate PDFs on publish
                                pdf_report_data = prepare_report_data(report)
                                generate_and_store_report_pdfs(dexa_system, pdf_report_data)
                                st.rerun()
                    else:
                        st.button(f"✅ Published", key=f"published_{report['report_id']}_{i}", disabled=True)
                
                with col3:
                    if st.button(f"📄 Generate PDFs", key=f"generate_{report['report_id']}_{i}"):
                        pdf_report_data = prepare_report_data(report)
                        generate_and_store_report_pdfs(dexa_system, pdf_report_data)
                        st.markdown('<div class="success-box">✅ PDFs generated! Check download buttons below.</div>', unsafe_allow_html=True)
                
                # Show download buttons if PDFs exist for this report - UPDATED WITH EYE ICONS
                st.markdown("---")
                st.markdown("### 📄 PDF Options")
                col_dl1, col_dl2 = st.columns(2)
                
                with col_dl1:
                    a4_key = f"a4_{report['report_id']}"
                    if a4_key in st.session_state.generated_pdfs:
                        col_dl1a, col_dl1b, col_dl1c = st.columns([2, 1, 1])
                        with col_dl1a:
                            st.write("**A4 Format PDF**")
                        with col_dl1b:
                            st.download_button(
                                label="📥 Download",
                                data=st.session_state.generated_pdfs[a4_key],
                                file_name=f"dexa_report_{report['report_id']}_A4.pdf",
                                mime="application/pdf",
                                key=f"dl_a4_{report['report_id']}_{i}"
                            )
                        with col_dl1c:
                            if create_eye_icon_button("Preview", f"preview_a4_{report['report_id']}_{i}"):
                                st.session_state.show_pdf_preview = True
                                st.session_state.preview_pdf_data = st.session_state.generated_pdfs[a4_key]
                                st.session_state.preview_pdf_title = f"DEXA Report {report['report_id']} - A4"
                                st.rerun()
                    else:
                        st.info("A4 PDF not generated yet")
                
                with col_dl2:
                    a5_key = f"a5_{report['report_id']}"
                    if a5_key in st.session_state.generated_pdfs:
                        col_dl2a, col_dl2b, col_dl2c = st.columns([2, 1, 1])
                        with col_dl2a:
                            st.write("**A5 Format PDF**")
                        with col_dl2b:
                            st.download_button(
                                label="📥 Download",
                                data=st.session_state.generated_pdfs[a5_key],
                                file_name=f"dexa_report_{report['report_id']}_A5.pdf",
                                mime="application/pdf",
                                key=f"dl_a5_{report['report_id']}_{i}"
                            )
                        with col_dl2c:
                            if create_eye_icon_button("Preview", f"preview_a5_{report['report_id']}_{i}"):
                                st.session_state.show_pdf_preview = True
                                st.session_state.preview_pdf_data = st.session_state.generated_pdfs[a5_key]
                                st.session_state.preview_pdf_title = f"DEXA Report {report['report_id']} - A5"
                                st.rerun()
                    else:
                        st.info("A5 PDF not generated yet")
    else:
        st.info("No reports created today.")
    
    # Show all published reports (read-only) - UPDATED WITH EYE ICONS
    st.subheader("📋 All Published Reports (Read-Only)")
    st.info("📚 These reports are published and can no longer be edited. Use the Version History tab to view previous versions.")
    
    all_reports = get_user_reports(st.session_state.user['user_id'], st.session_state.user['hospital_id'])
    
    if all_reports:
        for i, report in enumerate(all_reports):
            with st.expander(f"📋 {report['first_name']} {report['last_name']} - {report['report_id']} (Published: {report.get('published_at', 'N/A')})"):
                display_report_summary(report)
                
                # Show version count
                versions = get_report_versions(report['report_id'])
                st.info(f"📚 {len(versions)} versions available")
                
                # Show stored files - UPDATED WITH EYE ICONS
                stored_files = get_supabase_files_by_report(report['report_id'])
                if stored_files:
                    st.subheader("📁 Stored PDF Files")
                    for j, file in enumerate(stored_files):
                        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                        with col1:
                            st.write(f"**{file['filename']}** ({file['file_format']}) - {file['file_size_kb']:.1f} KB")
                        with col2:
                            st.download_button(
                                label="📥 Download",
                                data=requests.get(file['file_url']).content,
                                file_name=file['filename'],
                                mime="application/pdf",
                                key=f"download_{file['unique_filename']}_{i}_{j}"
                            )
                        with col3:
                            if create_eye_icon_button("Preview", f"cloud_preview_{file['unique_filename']}_{i}_{j}"):
                                st.session_state.show_pdf_preview = True
                                st.session_state.preview_pdf_data = requests.get(file['file_url']).content
                                st.session_state.preview_pdf_title = f"Cloud: {file['filename']}"
                                st.rerun()
                        with col4:
                            st.write(f"🔗 [Link]({file['file_url']})")
                
                # Export options
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"📄 A4 PDF", key=f"export_a4_{report['report_id']}_{i}"):
                        export_report_pdf(dexa_system, report['report_id'], 'A4')
                with col2:
                    if st.button(f"📄 A5 PDF", key=f"export_a5_{report['report_id']}_{i}"):
                        export_report_pdf(dexa_system, report['report_id'], 'A5')
    else:
        st.info("No published reports found.")

def display_report_summary(report):
    """Display report summary"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Total Mass", f"{report['total_mass']} kg")
        st.metric("Fat Mass", f"{report['fat_mass']} kg")
        st.metric("Lean Mass", f"{report['lean_mass']} kg")
        st.metric("Bone Mass", f"{report['bone_mass']} kg")
    
    with col2:
        st.metric("Body Fat %", f"{report['body_fat_percentage']}%")
        st.metric("Muscle Mass", f"{report['muscle_mass_almi']} kg/m²")
        st.metric("Bone Density", f"{report['bone_density_t_score']}")
        st.metric("Visceral Fat", f"{report['visceral_fat_area']} cm²")

def generate_and_store_report_pdfs(dexa_system, report_data):
    """Generate and store PDF reports in cloud - without download buttons"""
    report_id = report_data['report_id']
    
    # Generate A4 PDF
    try:
        pdf_a4 = dexa_system.generate_pdf(report_data, 'A4')
        if pdf_a4:
            success = dexa_system.save_to_supabase_storage(
                pdf_a4, 
                f"{report_id}_A4.pdf",
                report_id,
                'A4'
            )
            st.session_state.generated_pdfs[f"a4_{report_id}"] = pdf_a4
            st.success("✅ A4 PDF generated and stored!")
        else:
            pass
    except Exception as e:
        pass
    
    # Generate A5 PDF
    try:
        pdf_a5 = dexa_system.generate_pdf(report_data, 'A5')
        if pdf_a5:
            success = dexa_system.save_to_supabase_storage(
                pdf_a5, 
                f"{report_id}_A5.pdf",
                report_id,
                'A5'
            )
            st.session_state.generated_pdfs[f"a5_{report_id}"] = pdf_a5
            st.success("✅ A5 PDF generated and stored!")
        else:
            st.error("❌ Failed to generate A5 PDF")
    except Exception as e:
        st.error(f"❌ Error generating A5 PDF: {str(e)}")

def export_report_pdf(dexa_system, report_id, page_size):
    """Export existing report as PDF with proper error handling"""
    try:
        # Fetch report data
        conn = get_db_connection()
        if not conn:
            return
            
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT r.*, p.first_name, p.last_name, p.age, p.gender
            FROM dexa_reports r 
            JOIN patients p ON r.patient_id = p.patient_id 
            WHERE r.report_id = %s
        """, (report_id,))
        
        report = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not report:
            st.error(f"❌ Report {report_id} not found")
            return
        
        # Prepare report data for PDF generation
        report_data = prepare_report_data(report)
        
        # Generate PDF
        pdf_bytes = dexa_system.generate_pdf(report_data, page_size)
        
        if pdf_bytes:
            # Store in session state for later access
            session_key = f"{page_size.lower()}_{report_id}"
            st.session_state.generated_pdfs[session_key] = pdf_bytes
            
            # Create download and view buttons - UPDATED WITH EYE ICONS
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                st.download_button(
                    label=f"📥 Download {page_size}",
                    data=pdf_bytes,
                    file_name=f"dexa_report_{report_id}_{page_size}.pdf",
                    mime="application/pdf",
                    key=f"export_{report_id}_{page_size}_{datetime.now().timestamp()}"
                )
            with col2:
                if create_eye_icon_button(f"Preview {page_size}", f"export_preview_{report_id}_{page_size}"):
                    st.session_state.show_pdf_preview = True
                    st.session_state.preview_pdf_data = pdf_bytes
                    st.session_state.preview_pdf_title = f"Export: {report_id} - {page_size}"
                    st.rerun()
            with col3:
                st.info(f"✅ {page_size} PDF Ready")
            
            # Also save to cloud storage
            success = dexa_system.save_to_supabase_storage(
                pdf_bytes, 
                f"{report_id}_{page_size}.pdf",
                report_id,
                page_size
            )
            
            if success:
                st.success(f"✅ {page_size} PDF saved to cloud storage")
            else:
                st.warning(f"⚠️ PDF generated but cloud save failed")
        else:
            st.error("❌ Failed to generate PDF")
            
    except Exception as e:
        st.error(f"❌ Error exporting report: {str(e)}")

def show_edit_report_form(dexa_system, report_id, report_data):
    """Show form for editing an existing report"""
    st.markdown(f'<div class="section-header">✏️ Edit Report: {report_id}</div>', unsafe_allow_html=True)
    
    # Get current images
    current_images = dexa_system._get_report_images_for_pdf(report_id)
    
    # Safely extract values from report_data with defaults
    def safe_get(key, default=None):
        return report_data.get(key, default)
    
    # Initialize form - this must be at the top level
    with st.form("edit_report_form"):
        st.markdown('<div class="section-header">👤 Patient Information</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        
        with col1:
            patient_id = st.text_input("🆔 Patient ID*", value=safe_get('patient_id', '000480'))
            first_name = st.text_input("👤 First Name*", value=safe_get('first_name', 'BRI'))
            last_name = st.text_input("👤 Last Name*", value=safe_get('last_name', 'K'))
            age = st.number_input("🎂 Age*", min_value=1, max_value=120, value=int(safe_get('age', 36)))
            gender = st.selectbox("⚧ Gender*", ["M", "F"], index=0 if safe_get('gender', 'M') == 'M' else 1)
        
        with col2:
            report_id_display = st.text_input("📋 Report ID*", value=report_id, disabled=True)
            report_date = st.date_input("📅 Report Date*", value=safe_get('report_date', date.today()))
            height = st.number_input("📏 Height (cm)*", min_value=100.0, max_value=250.0, value=float(safe_get('height', 171.0)))
        
        st.markdown('<div class="section-header">⚖️ Body Composition</div>', unsafe_allow_html=True)
        col3, col4 = st.columns(2)
        
        with col3:
            total_mass = st.number_input("⚖️ Total Mass (kg)*", min_value=0.0, value=float(safe_get('total_mass', 104.6)))
            fat_mass = st.number_input("🩸 Fat Mass (kg)*", min_value=0.0, value=float(safe_get('fat_mass', 39.79)))
            lean_mass = st.number_input("💪 Lean Mass (kg)*", min_value=0.0, value=float(safe_get('lean_mass', 61.84)))
            bone_mass = st.number_input("🦴 Bone Mass (kg)*", min_value=0.0, value=float(safe_get('bone_mass', 2.94)))
        
        with col4:
            body_fat_percentage = st.number_input("📊 Body Fat Percentage*", min_value=0.0, max_value=100.0, value=float(safe_get('body_fat_percentage', 38.0)))
            muscle_mass_almi = st.number_input("🏋️ Muscle Mass ALMI (kg/m²)*", min_value=0.0, value=float(safe_get('muscle_mass_almi', 10.23)))
            bone_density_t_score = st.number_input("🦴 Bone Density T-Score*", value=float(safe_get('bone_density_t_score', -0.6)))
            z_score = st.number_input("📈 Z-Score*", value=float(safe_get('z_score', -0.6)))
        
        st.markdown('<div class="section-header">📈 Additional Metrics</div>', unsafe_allow_html=True)
        col5, col6 = st.columns(2)
        
        with col5:
            visceral_fat_area = st.number_input("🎯 Visceral Fat Area (cm²)*", min_value=0.0, value=float(safe_get('visceral_fat_area', 170.0)))
            ag_ratio = st.number_input("📐 A/G Ratio*", min_value=0.0, value=float(safe_get('ag_ratio', 1.23)))
            ffmi = st.number_input("💪 FFMI (kg/m²)*", min_value=0.0, value=float(safe_get('ffmi', 20.67)))
        
        with col6:
            # FIX: Handle case sensitivity and provide safe default index
            fracture_risk_options = ["LOW", "MODERATE", "HIGH"]
            current_fracture_risk = safe_get('fracture_risk', 'LOW').upper()
            fracture_risk_index = fracture_risk_options.index(current_fracture_risk) if current_fracture_risk in fracture_risk_options else 0
            fracture_risk = st.selectbox("⚠️ Fracture Risk*", fracture_risk_options, index=fracture_risk_index)
            
            muscle_loss_risk_options = ["LOW", "MODERATE", "HIGH"]
            current_muscle_loss_risk = safe_get('muscle_loss_risk', 'LOW').upper()
            muscle_loss_risk_index = muscle_loss_risk_options.index(current_muscle_loss_risk) if current_muscle_loss_risk in muscle_loss_risk_options else 0
            muscle_loss_risk = st.selectbox("💪 Muscle Loss Risk*", muscle_loss_risk_options, index=muscle_loss_risk_index)
        
        # Regional Composition Data
        st.markdown('<div class="section-header">💪 Arms Composition</div>', unsafe_allow_html=True)
        
        col7, col8, col9 = st.columns(3)
        with col7:
            right_arm_fat = st.number_input("Right Arm Fat (kg)", min_value=0.0, value=float(safe_get('right_arm_fat', 3.2)))
            left_arm_fat = st.number_input("Left Arm Fat (kg)", min_value=0.0, value=float(safe_get('left_arm_fat', 3.1)))
        with col8:
            right_arm_lean = st.number_input("Right Arm Lean (kg)", min_value=0.0, value=float(safe_get('right_arm_lean', 2.8)))
            left_arm_lean = st.number_input("Left Arm Lean (kg)", min_value=0.0, value=float(safe_get('left_arm_lean', 2.7)))
        with col9:
            right_arm_bmc = st.number_input("Right Arm BMC (kg)", min_value=0.0, value=float(safe_get('right_arm_bmc', 0.15)))
            left_arm_bmc = st.number_input("Left Arm BMC (kg)", min_value=0.0, value=float(safe_get('left_arm_bmc', 0.14)))
        
        st.markdown('<div class="section-header">🦵 Legs Composition</div>', unsafe_allow_html=True)
        
        col10, col11, col12 = st.columns(3)
        with col10:
            right_leg_fat = st.number_input("Right Leg Fat (kg)", min_value=0.0, value=float(safe_get('right_leg_fat', 8.5)))
            left_leg_fat = st.number_input("Left Leg Fat (kg)", min_value=0.0, value=float(safe_get('left_leg_fat', 8.3)))
        with col11:
            right_leg_lean = st.number_input("Right Leg Lean (kg)", min_value=0.0, value=float(safe_get('right_leg_lean', 7.2)))
            left_leg_lean = st.number_input("Left Leg Lean (kg)", min_value=0.0, value=float(safe_get('left_leg_lean', 7.1)))
        with col12:
            right_leg_bmc = st.number_input("Right Leg BMC (kg)", min_value=0.0, value=float(safe_get('right_leg_bmc', 0.45)))
            left_leg_bmc = st.number_input("Left Leg BMC (kg)", min_value=0.0, value=float(safe_get('left_leg_bmc', 0.44)))
        
        st.markdown('<div class="section-header">🦺 Trunk Composition</div>', unsafe_allow_html=True)
        
        col13, col14, col15 = st.columns(3)
        with col13:
            trunk_fat = st.number_input("Trunk Fat (kg)", min_value=0.0, value=float(safe_get('trunk_fat', 18.5)))
        with col14:
            trunk_lean = st.number_input("Trunk Lean (kg)", min_value=0.0, value=float(safe_get('trunk_lean', 25.8)))
        with col15:
            trunk_bmc = st.number_input("Trunk BMC (kg)", min_value=0.0, value=float(safe_get('trunk_bmc', 0.85)))
        
        # Image Update Section
        st.markdown('<div class="section-header">🖼️ Update Medical Images</div>', unsafe_allow_html=True)
        
        col_img1, col_img2 = st.columns(2)
        
        with col_img1:
            st.subheader("AP-Spine Image")
            new_ap_spine = st.file_uploader("Update AP-Spine Image", type=['png', 'jpg', 'jpeg'], key="edit_ap_spine")
            if current_images.get('ap_spine'):
                st.info("✅ Current image exists")
            
            st.subheader("Right Femur Image")
            new_right_femur = st.file_uploader("Update Right Femur Image", type=['png', 'jpg', 'jpeg'], key="edit_right_femur")
            if current_images.get('right_femur'):
                st.info("✅ Current image exists")
            
            st.subheader("Full Body Image")
            new_full_body = st.file_uploader("Update Full Body Image", type=['png', 'jpg', 'jpeg'], key="edit_full_body")
            if current_images.get('full_body'):
                st.info("✅ Current image exists")
        
        with col_img2:
            st.subheader("Left Femur Image")
            new_left_femur = st.file_uploader("Update Left Femur Image", type=['png', 'jpg', 'jpeg'], key="edit_left_femur")
            if current_images.get('left_femur'):
                st.info("✅ Current image exists")
            
            st.subheader("Fat Distribution Image")
            new_fat_dist = st.file_uploader("Update Fat Distribution Image", type=['png', 'jpg', 'jpeg'], key="edit_fat_dist")
            if current_images.get('fat_distribution'):
                st.info("✅ Current image exists")
        
        # Edit reason for version control
        edit_reason = st.text_area("📝 Edit Reason", placeholder="Describe what changes you made and why...", help="This will be recorded in the version history")
        
        # FIX: Create a container to store form data and handle submission
        form_data = {}
        
        # Store all form data in a dictionary
        form_data.update({
            'patient_id': patient_id,
            'first_name': first_name,
            'last_name': last_name,
            'age': age,
            'gender': gender,
            'report_date': report_date,
            'height': height,
            'total_mass': total_mass,
            'fat_mass': fat_mass,
            'lean_mass': lean_mass,
            'bone_mass': bone_mass,
            'body_fat_percentage': body_fat_percentage,
            'muscle_mass_almi': muscle_mass_almi,
            'bone_density_t_score': bone_density_t_score,
            'z_score': z_score,
            'visceral_fat_area': visceral_fat_area,
            'ag_ratio': ag_ratio,
            'ffmi': ffmi,
            'fracture_risk': fracture_risk,
            'muscle_loss_risk': muscle_loss_risk,
            'right_arm_fat': right_arm_fat,
            'right_arm_lean': right_arm_lean,
            'right_arm_bmc': right_arm_bmc,
            'left_arm_fat': left_arm_fat,
            'left_arm_lean': left_arm_lean,
            'left_arm_bmc': left_arm_bmc,
            'right_leg_fat': right_leg_fat,
            'right_leg_lean': right_leg_lean,
            'right_leg_bmc': right_leg_bmc,
            'left_leg_fat': left_leg_fat,
            'left_leg_lean': left_leg_lean,
            'left_leg_bmc': left_leg_bmc,
            'trunk_fat': trunk_fat,
            'trunk_lean': trunk_lean,
            'trunk_bmc': trunk_bmc,
            'edit_reason': edit_reason,
            'new_ap_spine': new_ap_spine,
            'new_right_femur': new_right_femur,
            'new_left_femur': new_left_femur,
            'new_full_body': new_full_body,
            'new_fat_dist': new_fat_dist
        })
        
        # FIX: Proper submit buttons inside the form
        col16, col17, col18 = st.columns(3)
        
        with col16:
            save_changes = st.form_submit_button("💾 Save Changes")
        with col17:
            save_and_publish = st.form_submit_button("🚀 Save & Publish")
        with col18:
            cancel_edit = st.form_submit_button("❌ Cancel Edit")
        
        # Handle form submission INSIDE the form context
        if save_changes or save_and_publish:
            # Validate required fields
            required_fields = {
                "Patient ID": form_data['patient_id'],
                "First Name": form_data['first_name'],
                "Last Name": form_data['last_name'],
                "Height": form_data['height']
            }
            
            missing_fields = [field for field, value in required_fields.items() if not value]
            if missing_fields:
                st.error(f"❌ Please fill in: {', '.join(missing_fields)}")
                st.stop()
            
            if not form_data['edit_reason'].strip():
                st.error("❌ Please provide an edit reason for version control")
                st.stop()
            
            # Prepare updated report data
            updated_report_data = {
                'patient_id': form_data['patient_id'],
                'report_id': report_id,
                'first_name': form_data['first_name'],
                'last_name': form_data['last_name'],
                'age': form_data['age'],
                'gender': form_data['gender'],
                'height': form_data['height'],
                'report_date': form_data['report_date'],
                'total_mass': form_data['total_mass'],
                'fat_mass': form_data['fat_mass'],
                'lean_mass': form_data['lean_mass'],
                'bone_mass': form_data['bone_mass'],
                'body_fat_percentage': form_data['body_fat_percentage'],
                'muscle_mass_almi': form_data['muscle_mass_almi'],
                'bone_density_t_score': form_data['bone_density_t_score'],
                'z_score': form_data['z_score'],
                'visceral_fat_area': form_data['visceral_fat_area'],
                'ag_ratio': form_data['ag_ratio'],
                'ffmi': form_data['ffmi'],
                'fracture_risk': form_data['fracture_risk'],
                'muscle_loss_risk': form_data['muscle_loss_risk'],
                
                # Regional composition
                'right_arm_fat': form_data['right_arm_fat'],
                'right_arm_lean': form_data['right_arm_lean'],
                'right_arm_bmc': form_data['right_arm_bmc'],
                'left_arm_fat': form_data['left_arm_fat'],
                'left_arm_lean': form_data['left_arm_lean'],
                'left_arm_bmc': form_data['left_arm_bmc'],
                'right_leg_fat': form_data['right_leg_fat'],
                'right_leg_lean': form_data['right_leg_lean'],
                'right_leg_bmc': form_data['right_leg_bmc'],
                'left_leg_fat': form_data['left_leg_fat'],
                'left_leg_lean': form_data['left_leg_lean'],
                'left_leg_bmc': form_data['left_leg_bmc'],
                'trunk_fat': form_data['trunk_fat'],
                'trunk_lean': form_data['trunk_lean'],
                'trunk_bmc': form_data['trunk_bmc'],
                
                'created_by': st.session_state.user['user_id'],
                'is_published': bool(save_and_publish) or safe_get('is_published', False)
            }
            
            # Update report in database
            if update_existing_report(updated_report_data):
                # Save new images if any were uploaded
                update_images = {
                    'ap_spine': form_data['new_ap_spine'],
                    'right_femur': form_data['new_right_femur'],
                    'left_femur': form_data['new_left_femur'],
                    'full_body': form_data['new_full_body'],
                    'fat_distribution': form_data['new_fat_dist']
                }
                
                # Remove None values (images that weren't updated)
                update_images = {k: v for k, v in update_images.items() if v is not None}
                
                if update_images:
                    dexa_system._save_report_images(report_id, update_images)
                
                # Save new version
                save_report_version(
                    report_id, 
                    updated_report_data, 
                    st.session_state.user['user_id'], 
                    form_data['edit_reason']
                )
                
                if save_and_publish:
                    publish_report_func(report_id)
                    st.success("✅ Report updated, new version saved, and published!")
                    # Generate new PDFs
                    pdf_report_data = prepare_report_data(updated_report_data)
                    generate_and_store_report_pdfs(dexa_system, pdf_report_data)
                else:
                    st.success("✅ Report updated and new version saved!")
                
                # Clear edit state
                st.session_state.editing_report = None
                st.session_state.edit_report_data = None
                
                st.balloons()
                st.rerun()
        
        # Handle cancel inside form context
        if cancel_edit:
            st.session_state.editing_report = None
            st.session_state.edit_report_data = None
            st.rerun()

def show_admin_user_management(user):
    """Admin user management"""
    st.markdown('<div class="section-header">👥 User Management</div>', unsafe_allow_html=True)
    
    # Create new user form
    with st.form("create_user_form"):
        st.markdown("### Create New User")
        col1, col2 = st.columns(2)
        
        with col1:
            full_name = st.text_input("Full Name")
            username = st.text_input("Username")
        
        with col2:
            mobile_number = st.text_input("Mobile Number")
            password = st.text_input("Password", type="password")
            user_type = st.selectbox("User Type", ["user", "admin"])
        
        if st.form_submit_button("Create User"):
            if all([full_name, username, mobile_number, password]):
                if not validate_phone(mobile_number):
                    st.error("Invalid mobile number format")
                elif not validate_password(password):
                    st.error("Password must be 6 or more characters")
                else:
                    user_data = {
                        'hospital_id': user['hospital_id'],
                        'username': username,
                        'password': password,
                        'user_type': user_type,
                        'full_name': full_name,
                        'mobile_number': mobile_number
                    }
                    
                    if create_user(user_data):
                        st.success("User created successfully!")
                    else:
                        st.error("Error creating user. Username may already exist.")
            else:
                st.error("Please fill all fields")
    
    # User list
    st.markdown("### Existing Users")
    users = get_hospital_users(user['hospital_id'])
    
    if users:
        for user_item in users:
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                st.write(f"**{user_item['full_name']}** ({user_item['username']})")
                st.write(f"Mobile: {user_item['mobile_number']} | Type: {user_item['user_type']}")
            
            with col2:
                if user_item['user_id'] != user['user_id']:
                    if st.button("Reset Password", key=f"reset_{user_item['user_id']}"):
                        # Simple password reset
                        new_password = "temp123"
                        conn = get_db_connection()
                        if conn:
                            cursor = conn.cursor()
                            cursor.execute("UPDATE users SET password_hash = %s WHERE user_id = %s", 
                                         (hash_password(new_password), user_item['user_id']))
                            conn.commit()
                            cursor.close()
                            conn.close()
                            st.success(f"Password reset to: {new_password}")
            
            with col3:
                if user_item['user_id'] != user['user_id']:
                    if st.button("Delete", key=f"delete_{user_item['user_id']}"):
                        conn = get_db_connection()
                        if conn:
                            cursor = conn.cursor()
                            try:
                                cursor.execute("DELETE FROM patient_user_mapping WHERE user_id = %s", (user_item['user_id'],))
                                cursor.execute("DELETE FROM users WHERE user_id = %s", (user_item['user_id'],))
                                conn.commit()
                                st.success("User deleted successfully!")
                                st.rerun()
                            except Exception as e:
                                st.error("Error deleting user")
                            finally:
                                cursor.close()
                                conn.close()
    else:
        st.info("No users found.")

def show_admin_reports(dexa_system, user):
    """Admin reports view"""
    st.markdown('<div class="section-header">📋 All Reports</div>', unsafe_allow_html=True)
    
    reports = get_user_reports(user['user_id'], user['hospital_id'])
    
    if reports:
        for report in reports:
            with st.expander(f"📄 {report['first_name']} {report['last_name']} - {report['report_id']} ({report['report_date']})"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Total Mass", f"{report['total_mass']} kg")
                    st.metric("Fat Mass", f"{report['fat_mass']} kg")
                    st.metric("Lean Mass", f"{report['lean_mass']} kg")
                
                with col2:
                    st.metric("Body Fat %", f"{report['body_fat_percentage']}%")
                    st.metric("Muscle Mass", f"{report['muscle_mass_almi']} kg/m²")
                    st.metric("Bone Density", f"{report['bone_density_t_score']}")
                
                # PDF generation
                col3, col4 = st.columns(2)
                with col3:
                    if st.button(f"📄 Generate A4 PDF", key=f"a4_{report['report_id']}"):
                        pdf_data = prepare_report_data(report)
                        pdf_bytes = dexa_system.generate_pdf(pdf_data, 'A4')
                        if pdf_bytes:
                            st.download_button(
                                label="📥 Download A4 PDF",
                                data=pdf_bytes,
                                file_name=f"dexa_report_{report['report_id']}_A4.pdf",
                                mime="application/pdf",
                                key=f"dl_a4_{report['report_id']}"
                            )
                
                with col4:
                    if st.button(f"📄 Generate A5 PDF", key=f"a5_{report['report_id']}"):
                        pdf_data = prepare_report_data(report)
                        pdf_bytes = dexa_system.generate_pdf(pdf_data, 'A5')
                        if pdf_bytes:
                            st.download_button(
                                label="📥 Download A5 PDF",
                                data=pdf_bytes,
                                file_name=f"dexa_report_{report['report_id']}_A5.pdf",
                                mime="application/pdf",
                                key=f"dl_a5_{report['report_id']}"
                            )
    else:
        st.info("No reports found.")

def show_version_history():
    """Show complete version history for reports"""
    st.markdown('<div class="section-header">🔄 Report Version History</div>', unsafe_allow_html=True)
    
    # Get all reports to select from
    all_reports = get_user_reports(st.session_state.user['user_id'], st.session_state.user['hospital_id'])
    
    if all_reports:
        report_options = {f"{r['first_name']} {r['last_name']} - {r['report_id']}": r['report_id'] for r in all_reports}
        selected_report = st.selectbox("Select Report", list(report_options.keys()))
        
        if selected_report:
            report_id = report_options[selected_report]
            versions = get_report_versions(report_id)
            
            if versions:
                st.subheader(f"Version History for {selected_report}")
                
                for version in versions:
                    with st.expander(f"Version {version['version_number']} - {version['created_at']}"):
                        st.write(f"**Edited by:** {version['edited_by']}")
                        st.write(f"**Reason:** {version['edit_reason']}")
                        
                        # Display version data
                        report_data = json.loads(version['report_data'])
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.metric("Total Mass", f"{report_data.get('total_mass', 0)} kg")
                            st.metric("Fat Mass", f"{report_data.get('fat_mass', 0)} kg")
                            st.metric("Lean Mass", f"{report_data.get('lean_mass', 0)} kg")
                        
                        with col2:
                            st.metric("Body Fat %", f"{report_data.get('body_fat_percentage', 0)}%")
                            st.metric("Muscle Mass", f"{report_data.get('muscle_mass_almi', 0)} kg/m²")
                            st.metric("Bone Density", f"{report_data.get('bone_density_t_score', 0)}")
            else:
                st.info("No version history available for this report.")
    else:
        st.info("No reports available to show version history.")

def show_user_reports_page(dexa_system, user):
    """User reports page with help section moved to header"""
    st.markdown('<div class="section-header">📋 My Reports</div>', unsafe_allow_html=True)
    
    # User info and logout with help button in header
    col4, col5, col6 = st.columns([3, 1, 1])
    with col4:
        st.write(f"Welcome, **{user['full_name']}** ({user['user_type'].title()})")
    with col5:
        # Help button instead of expander
        if st.button("🆘 Help", use_container_width=True):
            st.session_state.show_help_section = not st.session_state.get('show_help_section', False)
            st.rerun()
    
    
    # Show help section if toggled
    if st.session_state.get('show_help_section', False):
        st.markdown("""
        
        
        **For technical issues or report access problems, please contact your hospital administrator:**
        
        - **Hospital:** {hospital_name}
        - **Phone:** {phone_number}
        - **Email:** {email}
        - **Address:** {address}
        
        **Common Issues:**
        - Can't see your reports? Contact admin to link your account
        - PDF download not working? Try refreshing the page
        - Forgot password? Admin can reset it for you
        
        **Note:** Only published reports are visible here. If you don't see expected reports, 
        they may still be in draft status or not assigned to your account.
        
        """.format(
            hospital_name=user['hospital_name'],
            phone_number=user['phone_number'],
            email=user['email'],
            address=user['address']
        ))
    
    # User reports - main content
    reports = get_user_reports(user['user_id'], user['hospital_id'])
    
    if reports:
        for report in reports:
            with st.expander(f"📄 {report['first_name']} {report['last_name']} - {report['report_id']} ({report['report_date']})"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Total Mass", f"{report['total_mass']} kg")
                    st.metric("Body Fat %", f"{report['body_fat_percentage']}%")
                    st.metric("Muscle Mass", f"{report['muscle_mass_almi']} kg/m²")
                
                with col2:
                    st.metric("Bone Density", f"{report['bone_density_t_score']}")
                    st.metric("Visceral Fat", f"{report['visceral_fat_area']} cm²")
                    st.metric("Status", "Published")
                
                # PDF download
                col3, col4 = st.columns(2)
                with col3:
                    if st.button(f"📄 Download A4 PDF", key=f"user_a4_{report['report_id']}"):
                        pdf_data = prepare_report_data(report)
                        pdf_bytes = dexa_system.generate_pdf(pdf_data, 'A4')
                        if pdf_bytes:
                            st.download_button(
                                label="📥 Download A4",
                                data=pdf_bytes,
                                file_name=f"dexa_report_{report['report_id']}_A4.pdf",
                                mime="application/pdf",
                                key=f"user_dl_a4_{report['report_id']}"
                            )
                
                with col4:
                    if st.button(f"📄 Download A5 PDF", key=f"user_a5_{report['report_id']}"):
                        pdf_data = prepare_report_data(report)
                        pdf_bytes = dexa_system.generate_pdf(pdf_data, 'A5')
                        if pdf_bytes:
                            st.download_button(
                                label="📥 Download A5",
                                data=pdf_bytes,
                                file_name=f"dexa_report_{report['report_id']}_A5.pdf",
                                mime="application/pdf",
                                key=f"user_dl_a5_{report['report_id']}"
                            )
    else:
        st.info("""
        No reports available. This could be because:
        
        - No reports have been published yet
        - Your account hasn't been linked to any patients
        - Reports are still in draft status
        
        Please contact your hospital administrator if you believe you should have access to reports.
        """)
def show_cloud_storage(dexa_system):
    """Show cloud PDF storage management"""
    st.markdown('<div class="section-header">☁️ Cloud PDF Storage (Supabase)</div>', unsafe_allow_html=True)
    
    # Storage info
    file_count, total_size_mb = dexa_system.get_storage_info()
    
    st.markdown(f"""
        <div class="info-box">
            <strong>☁️ Storage Provider:</strong> Supabase<br>
            <strong>💾 Total Size:</strong> {total_size_mb:.2f} MB<br>
            <strong>📄 Files:</strong> {file_count} PDF reports
        </div>
    """, unsafe_allow_html=True)
    
    # List stored reports - UPDATED WITH EYE ICONS
    reports = dexa_system.list_stored_reports()
    if reports:
        st.markdown(f'<div class="section-header">📋 Stored PDF Reports ({len(reports)} files)</div>', unsafe_allow_html=True)
        
        for i, report in enumerate(reports):
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            
            with col1:
                st.markdown(f"""
                    <div class="info-box">
                        <strong>{report['filename']}</strong><br>
                        <small>Report: {report['first_name']} {report['last_name']} ({report['report_id']})</small><br>
                        <small>Size: {report['file_size_kb']} KB | Format: {report['file_format']} | Uploaded: {report['created_at'].strftime('%Y-%m-%d %H:%M')}</small><br>
                        <small>URL: <a href="{report['file_url']}" target="_blank">View File</a></small>
                    </div>
                """, unsafe_allow_html=True)
            
            with col2:
                # Download from URL
                st.download_button(
                    label="📥 Download",
                    data=requests.get(report['file_url']).content,
                    file_name=report['filename'],
                    mime="application/pdf",
                    key=f"download_{report['unique_filename']}_{i}",
                    use_container_width=True
                )
            
            with col3:
                # Preview with eye icon
                if create_eye_icon_button("Preview", f"cloud_storage_preview_{report['unique_filename']}_{i}"):
                    st.session_state.show_pdf_preview = True
                    st.session_state.preview_pdf_data = requests.get(report['file_url']).content
                    st.session_state.preview_pdf_title = f"Cloud Storage: {report['filename']}"
                    st.rerun()
            
            with col4:
                st.write(f"🔗 [Link]({report['file_url']})")
    else:
        st.markdown("""
            <div class="warning-box">
                No PDF reports stored in cloud yet.
            </div>
        """, unsafe_allow_html=True)

def show_login_page():
    """Show clean login page without headers"""
    st.markdown("""
        <style>
        .login-container {
            max-width: 400px;
            margin: 100px auto;
            padding: 2rem;
            background: white;
            border-radius: 1rem;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        }
        </style>
    """, unsafe_allow_html=True)
    
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown('<div class="login-container">', unsafe_allow_html=True)
            st.markdown('<h2 style="text-align: center;">🔐 Hospital Login</h2>', unsafe_allow_html=True)
            
            with st.form("login_form"):
                username = st.text_input("👤 Username", placeholder="Enter your username")
                password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
                
                col4, col5 = st.columns(2)
                with col4:
                    login_btn = st.form_submit_button("🚀 Login", use_container_width=True)
                with col5:
                    if st.form_submit_button("👤 Register", use_container_width=True):
                        st.session_state.show_register = True
                        st.rerun()
                
                # Hospital registration option
                st.markdown("---")
                if st.form_submit_button("🏥 Register Hospital", use_container_width=True):
                    st.session_state.show_hospital_registration = True
                    st.rerun()
                
                if login_btn:
                    if username and password:
                        user = authenticate_user(username, password)
                        if user:
                            st.session_state.user = user
                            st.rerun()
                        else:
                            st.error("Invalid username or password")
                    else:
                        st.error("Please enter both username and password")
            
            st.markdown('</div>', unsafe_allow_html=True)

def show_hospital_registration_page():
    """Show hospital registration page"""
    st.markdown('<h2 style="text-align: center;">🏥 Hospital Registration</h2>', unsafe_allow_html=True)
    
    with st.form("hospital_registration"):
        st.markdown("### Hospital Information")
        
        col1, col2 = st.columns(2)
        with col1:
            hospital_name = st.text_input("Hospital Name*", placeholder="Enter hospital name")
            hospital_code = st.text_input("Hospital Code*", placeholder="Unique code for hospital")
            phone_number = st.text_input("Phone Number*", placeholder="10-digit phone number")
        
        with col2:
            address = st.text_area("Address*", placeholder="Full hospital address")
            email = st.text_input("Email*", placeholder="Hospital email address")
        
        st.markdown("### Admin Account")
        
        col3, col4 = st.columns(2)
        with col3:
            admin_name = st.text_input("Admin Name*", placeholder="Full name of administrator")
            admin_username = st.text_input("Admin Username*", placeholder="Choose username")
        
        with col4:
            admin_mobile = st.text_input("Admin Mobile*", placeholder="10-digit mobile number")
            admin_password = st.text_input("Admin Password*", type="password", placeholder="6+ characters")
            confirm_password = st.text_input("Confirm Password*", type="password", placeholder="Confirm password")
        
        col5, col6 = st.columns(2)
        with col5:
            register_btn = st.form_submit_button("🏥 Register Hospital", use_container_width=True)
        with col6:
            if st.form_submit_button("← Back to Login", use_container_width=True):
                st.session_state.show_hospital_registration = False
                st.rerun()
        
        if register_btn:
            # Validate inputs
            errors = []
            
            if not all([hospital_name, hospital_code, address, phone_number, email]):
                errors.append("All hospital fields are required")
            
            if not all([admin_name, admin_username, admin_mobile, admin_password, confirm_password]):
                errors.append("All admin fields are required")
            
            if not validate_phone(phone_number):
                errors.append("Invalid phone number format (10 digits required)")
            
            if not validate_phone(admin_mobile):
                errors.append("Invalid mobile number format (10 digits required)")
            
            if not validate_email(email):
                errors.append("Invalid email format")
            
            if not validate_password(admin_password):
                errors.append("Password must be 6 or more characters")
            
            if admin_password != confirm_password:
                errors.append("Passwords do not match")
            
            if errors:
                for error in errors:
                    st.error(error)
            else:
                # Create hospital
                hospital_data = {
                    'hospital_name': hospital_name,
                    'hospital_code': hospital_code,
                    'address': address,
                    'phone_number': phone_number,
                    'email': email
                }
                
                hospital_id = create_hospital(hospital_data)
                
                if hospital_id:
                    # Create admin user
                    user_data = {
                        'hospital_id': hospital_id,
                        'username': admin_username,
                        'password': admin_password,
                        'user_type': 'admin',
                        'full_name': admin_name,
                        'mobile_number': admin_mobile
                    }
                    
                    if create_user(user_data):
                        st.success("Hospital and admin account created successfully! Please login.")
                        st.session_state.show_hospital_registration = False
                        st.rerun()
                    else:
                        st.error("Error creating admin account")
                else:
                    st.error("Error creating hospital. Hospital code may already exist.")

def show_user_registration_page():
    """Show user registration page (for existing hospitals)"""
    st.markdown('<h2 style="text-align: center;">👤 User Registration</h2>', unsafe_allow_html=True)
    
    # Get hospitals for selection
    conn = get_db_connection()
    hospitals = []
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT hospital_id, hospital_name FROM hospitals")
        hospitals = cursor.fetchall()
        cursor.close()
        conn.close()
    
    if not hospitals:
        st.error("No hospitals registered yet. Please register a hospital first.")
        if st.button("← Back to Login"):
            st.session_state.show_register = False
            st.rerun()
        return
    
    hospital_options = {h['hospital_name']: h['hospital_id'] for h in hospitals}
    
    with st.form("user_registration"):
        selected_hospital = st.selectbox("Select Hospital*", list(hospital_options.keys()))
        hospital_id = hospital_options[selected_hospital]
        
        col1, col2 = st.columns(2)
        with col1:
            full_name = st.text_input("Full Name*", placeholder="Enter your full name")
            username = st.text_input("Username*", placeholder="Choose a username")
        
        with col2:
            mobile_number = st.text_input("Mobile Number*", placeholder="10-digit mobile number")
            password = st.text_input("Password*", type="password", placeholder="6+ characters")
            confirm_password = st.text_input("Confirm Password*", type="password", placeholder="Confirm password")
        
        col3, col4 = st.columns(2)
        with col3:
            register_btn = st.form_submit_button("👤 Register User", use_container_width=True)
        with col4:
            if st.form_submit_button("← Back to Login", use_container_width=True):
                st.session_state.show_register = False
                st.rerun()
        
        if register_btn:
            # Validate inputs
            errors = []
            
            if not all([full_name, username, mobile_number, password, confirm_password]):
                errors.append("All fields are required")
            
            if not validate_phone(mobile_number):
                errors.append("Invalid mobile number format (10 digits required)")
            
            if not validate_password(password):
                errors.append("Password must be 6 or more characters")
            
            if password != confirm_password:
                errors.append("Passwords do not match")
            
            if errors:
                for error in errors:
                    st.error(error)
            else:
                user_data = {
                    'hospital_id': hospital_id,
                    'username': username,
                    'password': password,
                    'user_type': 'user',
                    'full_name': full_name,
                    'mobile_number': mobile_number
                }
                
                if create_user(user_data):
                    st.success("User account created successfully! Please login.")
                    st.session_state.show_register = False
                    st.rerun()
                else:
                    st.error("Error creating user account. Username may already exist.")

if __name__ == "__main__":
    main()
