# DEXA Body Composition Report System

A comprehensive web application for managing DEXA (Dual-Energy X-ray Absorptiometry) scan reports with advanced PDF generation, cloud storage, and multi-user access control.

📋 Overview
This Streamlit-based application provides healthcare facilities with a complete solution for:

        DEXA Report Creation & Management - Comprehensive body composition analysis
        Professional PDF Generation - Pixel-perfect reports using WeasyPrint
        Cloud Storage Integration - Secure file storage with Supabase
        Multi-User Access Control - Role-based permissions (Admin/User)
        Version Control - Complete audit trail for report edits
        Hospital Management - Multi-tenant architecture

✨ Key Features

    🔐 Authentication & Security
    Multi-tier User System: Admin and Regular User roles
    Hospital Registration: Complete hospital onboarding
    Secure Login: SHA-256 password hashing
    Access Control: Patient-user mapping for data privacy
    
    📊 DEXA Report Management
    Comprehensive Data Capture: 50+ body composition metrics
    Regional Analysis: Arms, legs, trunk composition breakdown
    Medical Imaging: Support for AP-Spine, Femur, and body outline images
    Automated Assessments: Intelligent health risk evaluations
    Real-time Previews: Eye-icon previews for images and PDFs
    
    📄 Advanced PDF Generation
    WeasyPrint Engine: Exact HTML-to-PDF replication
    Multiple Formats: A4 and A5 page sizes
    Professional Templates: Medical-grade report formatting
    Dynamic Content: Automated recommendations and assessments
    
    ☁️ Cloud Storage
    Supabase Integration: Secure file storage
    Version Management: Track all PDF generations
    Storage Analytics: Usage monitoring and file management
    Direct Links: Shareable report URLs
    
    🔄 Version Control
    Edit Tracking: Complete change history
    Audit Trail: Who changed what and when
    Edit Restrictions: Same-day editing policy
    Reason Documentation: Mandatory change explanations

🏗️ System Architecture

    Database Schema
    MySQL Database: Relational data structure
    Multi-tenant Design: Hospital isolation
    Normalized Tables: Patients, Reports, Users, Measurements
    Image Storage: Base64 encoded medical images
    
    Technology Stack
    Frontend: Streamlit with custom CSS styling
    Backend: Python with MySQL connector
    PDF Generation: WeasyPrint with Jinja2 templates
    Cloud Storage: Supabase
    Authentication: Custom role-based system
    
    🚀 Installation & Setup
    Prerequisites:
    Python 3.8+
    MySQL Database
    Supabase Account
    Required Python packages

Environment Configuration:

        Create a .streamlit/secrets.toml file:
        
                  # Database Configuration
                  MYSQL_HOST = "your-mysql-host"
                  MYSQL_USER = "your-username"
                  MYSQL_PASSWORD = "your-password"
                  MYSQL_DATABASE = "dexa_reports"
                  MYSQL_PORT = 3306
                  
                  # Supabase Configuration
                  SUPABASE_URL = "your-supabase-url"
                  SUPABASE_KEY = "your-supabase-key"
                  SUPABASE_SERVICE_ROLE_KEY = "your-service-role-key"

Installation Steps:

    ->Clone the Repository:
        git clone <[repository-ur](https://github.com/Shiva1506/Dexa-report-managment-system)>
        cd dexa-report-system
    ->Install Dependencies:
        pip install -r requirements.txt
    ->Database Setup:
          # The application automatically initializes all required tables
    ->Run the Application
        streamlit run app.py

        
👥 User Roles & Permissions

      🎯 Administrator
              Full system access
              User management
              Hospital configuration
              Report creation and editing
              PDF generation and storage
              Version history access
      👤 Regular User
              View assigned reports
              Download PDF reports
              Limited to published reports only
              No editing capabilities

📊 Report Structure

      Core Metrics:
          Body Composition: Total mass, fat mass, lean mass, bone mass
          Health Indicators: Body fat percentage, visceral fat area
          Bone Health: T-score, Z-score, fracture risk assessment
          Muscle Analysis: ALMI, FFMI, muscle loss risk
          
      Regional Analysis:
          Arms: Right/left fat, lean, bone mineral content
          Legs: Right/left composition analysis
          Trunk: Core body composition
          Asymmetry Detection: Limb comparison analysis
      
      Automated Assessments:
          Body Zone Classification: Power Reserve, Optimal, Development zones
          Risk Profiling: Fracture, muscle loss, metabolic risks
          Personalized Recommendations: Nutrition and training guidance

🖼️ Image Management

    Supported Image Types:
        AP-Spine Scans: Anterior-Posterior spine images
        Femur Scans: Right and left femur analysis
        Body Outline: Full body composition maps
        Fat Distribution: Regional fat patterning
        
    Image Features:
        Base64 Storage: Secure database storage
        Preview Capability: Eye-icon preview system
        Format Conversion: Automatic PNG conversion for PDF compatibility
        Placeholder System: Fallback images for missing scans

🔧 Configuration
      Database Optimization:
          Connection pooling
          Transaction timeout management
          Retry logic for concurrent access
          Automatic schema updates
      
      PDF Generation Settings:
          WeasyPrint HTML rendering
          Custom CSS styling
          Static asset management
          Font and image embedding
      
      Storage Management:
          Supabase bucket configuration
          File size limits (10MB)
          Automatic cleanup procedures
          Storage analytics

📈 Usage Workflow

      1. Hospital Registration
          Register hospital details
          Create admin account
          Configure contact information
          
      2. User Management
          Add healthcare professionals
          Assign user roles
          Set access permissions
      
      3. Report Creation
          Enter patient demographics
          Input body composition data
          Upload medical images
          Add measurement details
      
      4. Quality Assurance
          Review automated assessments
          Verify image placements
          Check calculation accuracy
      
      5. Publication & Distribution
          Generate professional PDFs
          Store in cloud storage
          Share with patients/staff
          Maintain version history

🛠️ API Endpoints

      Authentication:
          POST /login - User authentication
          POST /register/hospital - Hospital registration
          POST /register/user - User account creation
      
      Report Management:
          POST /reports - Create new report
          PUT /reports/{id} - Update existing report
          GET /reports - List accessible reports
          GET /reports/{id}/pdf - Generate PDF report
      
      File Management:
          POST /storage/upload - Upload to cloud storage
          GET /storage/files - List stored files
          DELETE /storage/files/{id} - Remove files

🔒 Security Features

    Data Isolation: Hospital-specific data segregation
    Password Hashing: SHA-256 encryption
    Input Validation: Comprehensive field validation
    Access Logging: User activity tracking
    Session Management: Secure session handling

📱 Mobile Compatibility

    Responsive Design: Works on tablets and large phones
    Touch-Friendly: Optimized for touch interfaces
    Offline Capabilities: PDF download for offline viewing

🚨 Error Handling

    Graceful Degradation: System remains functional during partial failures
    User-Friendly Messages: Clear error explanations
    Automatic Retries: Database connection recovery
    Validation Feedback: Real-time form validation

📊 Monitoring & Analytics

    Storage Metrics: Cloud storage usage tracking
    User Activity: Report access patterns
    System Health: Database performance monitoring
    PDF Generation: Success/failure rate tracking

🔄 Update Procedures

    Database Migrations:
        Automatic schema updates
        Backward compatibility maintenance
        Data preservation during upgrades
        
    Application Updates:
        Zero-downtime deployments
        Configuration management
        Version compatibility checking

🤝 Support & Maintenance

    Technical Support:
        System administrator documentation
        Troubleshooting guides
        Performance optimization tips
    
    Regular Maintenance:
        Database optimization
        Storage cleanup
        Security updates
        Backup procedures


🎯 Getting Started

        Initial Setup: Configure environment variables and database
        Hospital Registration: Create your hospital organization
        User Creation: Add healthcare team members
        Report Testing: Create sample reports to verify functionality
        Production Deployment: Deploy to your healthcare facility
        Built for healthcare professionals  🏥💻

🏥 Hospital DEXA Report Management System - Project Structure

        dexa-report-system/
        ├── 📁 .streamlit/
        │   └── secrets.toml              # Environment variables
        ├── 📁 static/
        │   └── 📁 images/
        |         images.png
        ├── 📁 templates/
        │   └── report.html              # PDF template
        ├── app.py                       # Main application file
        ├── requirements.txt
        ├── README.md
        └── .gitignore

🗃️ Database Schema Structure
      Core Tables:
      
        -- Hospitals table
        hospitals
        ├── hospital_id (PK)
        ├── hospital_name
        ├── hospital_code
        ├── address
        ├── phone_number
        ├── email
        └── created_at
        
        -- Users table  
        users
        ├── user_id (PK)
        ├── hospital_id (FK)
        ├── username
        ├── password_hash
        ├── user_type (admin/user)
        ├── full_name
        ├── mobile_number
        └── created_at
        
        -- Patients table
        patients
        ├── patient_id (PK)
        ├── hospital_id (FK)
        ├── first_name
        ├── last_name
        ├── age
        ├── gender
        └── created_at
        
        -- Main DEXA reports table
        dexa_reports
        ├── report_id (PK)
        ├── patient_id (FK)
        ├── hospital_id (FK)
        ├── report_date
        ├── height
        ├── total_mass
        ├── fat_mass
        ├── lean_mass
        ├── bone_mass
        ├── body_fat_percentage
        ├── muscle_mass_almi
        ├── bone_density_t_score
        ├── z_score
        ├── visceral_fat_area
        ├── ag_ratio
        ├── ffmi
        ├── fracture_risk
        ├── muscle_loss_risk
        ├── regional_composition_fields (20+ columns)
        ├── is_published
        ├── created_by
        ├── created_at
        ├── last_edited
        └── edit_count
        
        -- Measurement tables
        ap_spine_measurements
        ├── measurement_id (PK)
        ├── report_id (FK)
        ├── region (L1, L2, L3, L4, L1-L4)
        ├── bmd
        ├── t_score
        └── z_score
        
        femur_measurements
        ├── measurement_id (PK)
        ├── report_id (FK)
        ├── side (RIGHT/LEFT)
        ├── region (NECK, TOTAL)
        ├── bmd
        ├── t_score
        └── z_score
        
        -- Image storage
        report_images
        ├── image_id (PK)
        ├── report_id (FK)
        ├── image_type (ap_spine, right_femur, left_femur, full_body, fat_distribution)
        ├── image_data (LONGTEXT - base64)
        └── image_format
        
        -- Version control
        report_versions
        ├── version_id (PK)
        ├── report_id (FK)
        ├── version_number
        ├── report_data (JSON)
        ├── edited_by
        ├── edit_reason
        └── created_at
        
        -- Cloud storage tracking
        supabase_files
        ├── file_id (PK)
        ├── report_id (FK)
        ├── filename
        ├── unique_filename
        ├── file_url
        ├── file_size_kb
        ├── file_format (A4/A5)
        ├── uploaded_by
        └── created_at
        
        -- Access control
        patient_user_mapping
        ├── mapping_id (PK)
        ├── patient_id (FK)
        ├── user_id (FK)
        └── created_at
        
🏗️ Application Architecture
        Core Modules Structure:
        
        app.py
        ├── 📦 WeasyPrintPDFGenerator Class
        │   ├── __init__()
        │   ├── _load_html_template()
        │   ├── _setup_base_urls()
        │   ├── _setup_static_images()
        │   ├── _process_uploaded_image()
        │   ├── _get_report_images_for_pdf()
        │   ├── _generate_assessments()
        │   ├── _generate_recommendations()
        │   ├── _calculate_regional_totals()
        │   ├── generate_pdf()
        │   ├── save_to_supabase_storage()
        │   └── get_storage_info()
        │
        ├── 📦 SupabaseStorageManager Class
        │   ├── __init__()
        │   ├── setup_supabase_storage()
        │   ├── upload_pdf_to_supabase()
        │   ├── list_supabase_files()
        │   ├── delete_supabase_file()
        │   └── get_storage_info()
        │
        ├── 🔧 Database Functions
        │   ├── get_db_connection()
        │   ├── init_database()
        │   ├── update_database_schema()
        │   ├── save_report_data()
        │   ├── update_existing_report()
        │   ├── prepare_report_data()
        │   └── get_report_versions()
        │
        ├── 🔐 Authentication Functions
        │   ├── hash_password()
        │   ├── authenticate_user()
        │   ├── create_hospital()
        │   ├── create_user()
        │   ├── link_patient_to_user()
        │   └── get_user_reports()
        │
        ├── 🎨 UI Components
        │   ├── show_login_page()
        │   ├── show_hospital_registration_page()
        │   ├── show_user_registration_page()
        │   ├── show_admin_interface()
        │   ├── show_user_interface()
        │   ├── create_new_report()
        │   ├── manage_reports()
        │   ├── show_edit_report_form()
        │   └── show_cloud_storage()
        │
        └── 🚀 Main Application Flow
            ├── main()
            ├── show_hospital_header()
            ├── show_admin_dashboard()
            └── show_user_reports_page()
            
📊 Data Flow Architecture


        1. Authentication Flow
        User Access → Login Validation → Role Detection → Interface Routing
             ↓              ↓                ↓               ↓
        [Login Page] → [Credential Check] → [Admin/User] → [Dashboard]
        
        2. Report Creation Flow
        Data Entry → Validation → Database Save → PDF Generation → Cloud Storage
             ↓           ↓            ↓             ↓               ↓
        [Form Input] → [Field Check] → [MySQL] → [WeasyPrint] → [Supabase]
        
        3. PDF Generation Pipeline
        Report Data → Template Rendering → Image Processing → PDF Creation → Storage
             ↓              ↓                 ↓               ↓             ↓
        [DB Query] → [Jinja2 HTML] → [Base64 Images] → [WeasyPrint] → [Supabase]
        
        4. Version Control System
        Edit Request → Data Validation → Version Creation → History Tracking
             ↓              ↓               ↓                 ↓
        [Edit Form] → [Change Check] → [JSON Snapshot] → [Version Table]
        
🎯 Component Responsibilities

        WeasyPrintPDFGenerator Class
          Purpose: Handle all PDF generation operations
          Key Methods:
            generate_pdf(): Main PDF creation entry point
            _generate_assessments(): Automated health assessments
            _generate_recommendations(): Personalized advice generation
            _process_uploaded_image(): Image optimization for PDF
          
        SupabaseStorageManager Class
          Purpose: Manage cloud file operations
          Key Methods:
              upload_pdf_to_supabase(): Secure file upload
              list_supabase_files(): Storage inventory management
              get_storage_info(): Usage analytics
        
        Database Layer
          Purpose: Data persistence and retrieval
          Key Functions:
            get_db_connection(): Connection pooling management
            save_report_data(): Complete report storage
            update_existing_report(): Safe data modifications
            
        Authentication Layer
          Purpose: User management and access control
          Key Functions:
            authenticate_user(): Secure login validation
            create_hospital(): Multi-tenant setup
            get_user_reports(): Role-based data filtering

🔄 Workflow Patterns
    Admin Workflow:

      Login → Dashboard → User Management → Report Creation → PDF Generation → Storage Management
        ↓         ↓            ↓               ↓                 ↓               ↓
      [Auth] → [Metrics] → [User CRUD] → [Data Entry] → [PDF Export] → [FileOps]
      User Workflow
      
      Login → My Reports → View Data → Download PDFs → Contact Support
        ↓         ↓          ↓           ↓               ↓
      [Auth] → [List] → [Read-Only] → [Export] → [Help System]
      Report Editing Workflow
      
      Select Report → Edit Data → Provide Reason → Save Version → Generate PDF → Update Storage
           ↓           ↓           ↓           ↓           ↓           ↓
      [Report List] → [Form] → [Audit Trail] → [History] → [WeasyPrint] → [Supabase
      
📁 File Structure Details

      Static Assets:
          static/images/
          ├── vital_insights_logo.png     # Brand logo for PDF headers
          ├── fingerprint_icon.png        # Patient identification icon  
          ├── body_outline.png           # Body composition diagram
          ├── ap_spine_placeholder.png   # Default spine scan image
          ├── femur_placeholder.png      # Default femur scan image
          └── fat_distribution_placeholder.png  # Fat mapping default
          
      Template System:
          templates/
          └── report.html                # Main PDF template
              ├── Header Section         # Hospital branding & patient info
              ├── Body Composition       # Metrics and visualizations
              ├── Regional Analysis      # Arms, legs, trunk breakdown
              ├── Medical Assessments    # Automated health evaluations
              ├── Recommendations        # Personalized advice
              ├── Image Placements       # Scan images and diagrams
              └── Footer                 # Legal and contact information
              
Configuration Files:

    .streamlit/
    ├── config.toml               # Streamlit appearance settings
    └── secrets.toml              # Sensitive environment variables
        ├── Database credentials
        ├── Supabase configuration  

🔐 Security Architecture
Access Control Matrix

Role        | Reports | Users | PDF Gen | Storage | Settings
------------|---------|-------|---------|---------|----------
Admin       | CRUD+   | CRUD+ | Full    | Full    | Full
User        | R       | -     | Export  | View    | -

Data Protection Layers:

    Application Layer: Role-based access control
    Database Layer: Hospital data isolation
    Storage Layer: Secure file permissions
    Network Layer: Encrypted communications

📈 Scalability Considerations

    Horizontal Scaling
    Stateless application design
    Database connection pooling
    External file storage
    Session-independent operations
    Performance Optimization
    Image compression for PDFs
    Database query optimization
    Cached static assets
    Lazy loading of reports

This structure provides a robust foundation for healthcare report management with clear separation of concerns, scalable architecture, and comprehensive feature coverage.

