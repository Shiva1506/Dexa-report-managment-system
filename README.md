🏥 DEXA Body Composition Report System
    A comprehensive web application for managing DEXA (Dual-Energy X-ray Absorptiometry) scan reports with advanced PDF generation, cloud storage, and multi-user access control.

📋 Overview

    This Streamlit-based application provides healthcare facilities with a complete solution for:
    DEXA Report Creation & Management - Comprehensive body composition analysis
    Professional PDF Generation - Pixel-perfect reports using Playwright
    Cloud Storage Integration - Secure file storage with Supabase
    Multi-User Access Control - Role-based permissions (Admin/User)
    Version Control - Complete audit trail for report edits
    Hospital Management - Multi-tenant architecture
    Email Notifications - Automated credential delivery and admin alerts

✨ Key Features
    🔐 Authentication & Security
    
        Multi-tier User System: Admin and Regular User roles
        Hospital Registration: Complete hospital onboarding
        Secure Login: SHA-256 password hashing
        Access Control: Patient-user mapping for data privacy
        Email Credential Delivery: Automated user registration with secure passwords

    📊 DEXA Report Management
      
          Comprehensive Data Capture: 50+ body composition metrics
          Regional Analysis: Arms, legs, trunk composition breakdown
          Medical Imaging: Support for AP-Spine, Femur, and body outline images
          Automated Assessments: Intelligent health risk evaluations
          Real-time Previews: Eye-icon previews for images and PDFs
      
   📄 Advanced PDF Generation
   
          Playwright Engine: High-quality HTML-to-PDF conversion
          Multiple Formats: A4 and A5 page sizes
          Professional Templates: Medical-grade report formatting
          Dynamic Content: Automated recommendations and assessments
          Base64 Image Support: Reliable image embedding in PDFs
          
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
      
   📧 Email Notification System
   
          User Registration: Automated credential delivery
          Admin Notifications: New user registration alerts
          SMTP Integration: Configurable email service
          HTML Templates: Professional email formatting
          Secure Password Generation: Temporary password creation

🏗️ System Architecture

    Database Schema
    
        MySQL Database: Relational data structure
        Multi-tenant Design: Hospital isolation
        Normalized Tables: Patients, Reports, Users, Measurements
        Image Storage: Base64 encoded medical images
        
    Technology Stack
    
        Frontend: Streamlit with custom CSS styling
        Backend: Python with MySQL connector
        PDF Generation: Playwright with Jinja2 templates
        Cloud Storage: Supabase
        Authentication: Custom role-based system
        Email: SMTP with HTML templates
        
🚀 Installation & Setup
    Prerequisites:
    
          Python 3.8+
          MySQL Database
          Supabase Account
          SMTP Email Service (Gmail, Outlook, etc.)
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
              
              # Email Configuration (for user notifications)
              SMTP_SERVER = "smtp.gmail.com"
              SMTP_PORT = 587
              SMTP_EMAIL = "your-email@gmail.com"
              SMTP_PASSWORD = "your-app-password"
              APP_URL = "https://your-app-url.streamlit.app"
          
    Installation Steps:
    
      Clone the Repository:

          git clone https://github.com/Shiva1506/Dexa-report-managment-system
          cd dexa-report-system
          
      Install Dependencies:
      
          pip install -r requirements.txt
          
    Run the Application:
    
            streamlit run dexa.py
            
👥 User Roles & Permissions

    🎯 Administrator
    
              Full system access
              User management with email notifications
              Hospital configuration
              Report creation and editing
              PDF generation and storage
              Version history access
              Email system configuration
        
    👤 Regular User
    
            View assigned reports
            Download PDF reports
            Access version history
            Limited to published reports only
            No editing capabilities
            Receive email credentials upon registration
    
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
          
                  AP-Spine Scans: Anterior-Posterior spine images
                  Femur Scans: Right and left femur analysis
                  Body Outline: Full body composition maps
                  Fat Distribution: Regional fat patterning
          
          Image Features:
          
                  Base64 Storage: Secure database storage
                  Preview Capability: Eye-icon preview system
                  Format Conversion: Automatic optimization for PDF compatibility
                  Placeholder System: Fallback images for missing scans
                  
    📧 Email System Features
    
            User Registration:
    
                Automated Credential Delivery: Secure temporary password
                Professional Templates: HTML email formatting
                Hospital Branding: Customized with hospital information
                Security Instructions: Password change reminders
                
            Admin Notifications:
    
                New User Alerts: Instant notification of registrations
                System Updates: Important administrative information
                Audit Trail: Email records of user activities
                
            Configuration:
    
                SMTP Support: Compatible with Gmail, Outlook, etc.
                App Passwords: Secure authentication
                HTML & Plain Text: Multi-format email support
                Customizable Templates: Branded communication
    
    🔧 Configuration
    Database Optimization:
    
            Connection pooling
            Transaction timeout management
            Retry logic for concurrent access
            Automatic schema updates
    
    PDF Generation Settings:
    
            Playwright HTML rendering
            Custom CSS styling
            Static asset management
            Font and image embedding
    
    Storage Management:
    
            Supabase bucket configuration
            File size limits (10MB)
            Automatic cleanup procedures
            Storage analytics
    
    Email Configuration:
    
            SMTP server settings
            HTML template customization
            Security best practices
            Delivery tracking

📈 Usage Workflow

    1. Hospital Registration
    
            Register hospital details
            Create admin account
            Configure contact information
            Set up email notifications

    2. User Management
       
            Add healthcare professionals
            Assign user roles
            Set access permissions
            Automated email credential delivery

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
            POST /register/user - User account creation with email
    
    Report Management:
    
            POST /reports - Create new report
            PUT /reports/{id} - Update existing report
            GET /reports - List accessible reports
            GET /reports/{id}/pdf - Generate PDF report
    
    File Management:
    
            POST /storage/upload - Upload to cloud storage
            GET /storage/files - List stored files
            DELETE /storage/files/{id} - Remove files
            
    Email Management:
    
            POST /email/test - Test email configuration
            POST /email/credentials - Send user credentials
            POST /email/notification - Send admin notifications

🔒 Security Features

        Data Isolation: Hospital-specific data segregation
        Password Hashing: SHA-256 encryption
        Input Validation: Comprehensive field validation
        Access Logging: User activity tracking
        Session Management: Secure session handling
        Email Security: App passwords and TLS encryption

🚨 Error Handling

        Graceful Degradation: System remains functional during partial failures
        User-Friendly Messages: Clear error explanations
        Automatic Retries: Database connection recovery
        Validation Feedback: Real-time form validation
        Email Failure Handling: Fallback options for notification failures

📊 Monitoring & Analytics

        Storage Metrics: Cloud storage usage tracking
        User Activity: Report access patterns
        System Health: Database performance monitoring
        PDF Generation: Success/failure rate tracking
        Email Delivery: Notification success rates

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
              Email configuration assistance
      
      Regular Maintenance:
      
              Database optimization
              Storage cleanup
              Security updates
              Backup procedures
              Email system monitoring

🎯 Getting Started

      Initial Setup: Configure environment variables and database
      Hospital Registration: Create your hospital organization
      Email Configuration: Set up SMTP for user notifications
      User Creation: Add healthcare team members with automated emails
      Report Testing: Create sample reports to verify functionality
      Production Deployment: Deploy to your healthcare facility
      Built for healthcare professionals 🏥💻
      Secure, Scalable, and Professional 🔒📈

🏥 Project Structure

      dexa-report-system/
      ├── 📁 .streamlit/
      │   └── secrets.toml              # Environment variables
      ├── 📁 static/
      │   └── 📁 images/
      │
      ├── 📁 templates/
      │   └── a.html                    # PDF template
      ├── dexa.py                       # Main application file
      ├── requirements.txt
      └── README.md
      
🗃️ Database Schema

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
          ├── email
          ├── mobile_number
          ├── is_first_login
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


Note: This system is designed for healthcare environments and includes enterprise-grade features for security, scalability, and professional reporting. The email notification system enhances user management while maintaining security best practices.
