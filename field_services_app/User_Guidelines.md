# Field Services Application - User Guidelines

*This document provides guidelines for both frontend and backend users of the Field Services Application. For a visual presentation format, this content can be converted to PowerPoint.*

## Table of Contents

1. [Introduction](#introduction)
2. [Backend User Guidelines (Admin)](#backend-user-guidelines-admin)
3. [Frontend User Guidelines](#frontend-user-guidelines)
4. [Common Workflows](#common-workflows)
5. [Troubleshooting](#troubleshooting)
6. [Known Issues and Limitations](#known-issues-and-limitations)

---

## Introduction

### About Field Services App

The Field Services Application is a comprehensive solution designed for fit-out project management, combining:

- Project and work order management
- Customer relationship management
- Inventory tracking
- Document management
- Communication tools
- Reporting and analytics
- Calendar with Hong Kong holidays integration
- Work Master system for standardized work items and packages

### System Architecture

- **Backend**: Django REST Framework
- **Database**: SQLite (Development) / PostgreSQL (Production)
- **Frontend**: React with TypeScript
- **API Documentation**: Swagger UI at `/swagger/`

---

## Backend User Guidelines (Admin)

### Accessing Admin Panel

1. Navigate to `http://localhost:8000/admin/`
2. Login with admin credentials:
   - Email: `admin@fieldservices.dev`
   - Password: `admin123`

### Managing Users

1. Navigate to **Users** in the admin sidebar
2. Options available:
   - Add new users
   - Edit existing user permissions
   - Assign roles (Admin, Manager, Technician)
   - Reset passwords

### Managing Projects

1. Navigate to **Projects** in the admin sidebar
2. Create new projects with:
   - Project name and description
   - Client information
   - Timeline (start/end dates)
   - Budget information
   - Assigned team members

### Managing Work Orders

1. Navigate to **Work Orders** in the admin sidebar
2. Create and assign work orders to technicians
3. Track status changes (New, In Progress, Completed, On Hold)
4. Link work orders to specific projects
5. Attach relevant documents

### Managing Inventory

1. Navigate to **Inventory** in the admin sidebar
2. Add/edit inventory items
3. Track stock levels
4. Link inventory to suppliers
5. Manage item locations

### Managing Work Master

1. Navigate to **Work Master** in the admin sidebar
2. Manage standardized work items:
   - Create work item templates with estimated hours
   - Assign skill levels (Basic, Intermediate, Advanced, Specialized)
   - Organize by categories
3. Create work packages:
   - Combine multiple work items
   - Set dependencies
   - Create templates for different contract types
4. Manage categories:
   - Create logical groupings
   - Set order priorities  
   
### Managing Technician Master List

1. Navigate to **Technicians** in the admin sidebar
2. Manage technician information:
   - Personal details (employee number, full name, nickname)
   - Contact information (phone, WhatsApp, email)
   - Specialties and certifications
   - Employment type (employment contract, sub-contractor, self-employed)
   - Cost information based on employment type
3. Track performance metrics:
   - Customer ratings
   - Punctuality rates
   - Completion rates
4. Compare cost efficiency across employment types:
   - Record cost metrics
   - Generate KPI reports
   - Analyze cost-effectiveness

### Document Management

1. Navigate to **Documents** in the admin sidebar
2. Upload and categorize documents
3. Control document versions
4. Manage permissions for document access

### Communication Tools

1. Navigate to **Communication** in the admin sidebar
2. Manage internal messaging
3. Set up WhatsApp integration
4. Create email templates

### Reports and Analytics

1. Navigate to **Reports** in the admin sidebar
2. Create custom dashboards
3. Set up scheduled reports
4. Define metrics to track

### Calendar Management

1. Navigate to **Calendar** in the admin sidebar
2. Manage Hong Kong holidays:
   - Update holiday data annually
   - Set bilingual display options (English/Chinese)
3. Configure calendar settings:
   - Default views
   - Working days
   - Business hours

---

## Frontend User Guidelines

### Logging In

1. Navigate to `http://localhost:3000/`
2. Enter your credentials:
   - Email address: `admin@fieldservices.dev`
   - Password: `admin123`
3. If you've forgotten your password, use the "Forgot Password" link
4. For quick development access, use the "Developer Login" option

### Dashboard Overview

The main dashboard provides:
- Quick navigation to all app areas
- Overview of active projects
- Work order status summary
- Recent activities
- Important notifications
- Inventory alerts

### Project Management

1. Navigate to Projects section from the sidebar
2. View project list with filtering options
3. Click on a project to view details:
   - Timeline
   - Budget tracking
   - Team members
   - Associated work orders
   - Documents
   - Communication history

### Work Order Management

1. Navigate to Work Orders section from the sidebar
2. Create new work orders
3. View assigned work orders
4. Update work order status
5. Add comments or documentation
6. Track time spent on work orders

### Inventory Management

1. Navigate to Inventory section from the sidebar
2. Search for items by name, category, or location
3. View stock levels
4. Request items for work orders
5. Report low stock items

### Document Access

1. Navigate to Documents section from the sidebar
2. Browse document categories
3. Search for specific documents using the search bar
4. Filter documents by category
5. View document details and history
6. Download documents
7. Upload new versions (if authorized)

*[SCREENSHOT: Documents list view showing file cards with document types, categories, and download options]*

### Calendar with Hong Kong Holidays

1. Navigate to Calendar section from the sidebar  
2. View calendar with Hong Kong SAR holidays highlighted in red
3. Click on a holiday to view details:
   - Name in English and Traditional Chinese
   - Date and description
   - Type of holiday
4. Schedule work around official holidays
5. Plan technician availability

*[SCREENSHOT: Calendar view showing April 2025 with Ching Ming Festival highlighted and detail dialog]*

### Work Master System

The Work Master system provides standardized work items and packages that can be used as templates for work orders.

1. Navigate to Work Master section from the sidebar
2. Access three main tabs:
   - **Work Packages**: Collections of work items for contract types
   - **Work Items**: Individual work tasks with specifications
   - **Categories**: Groups work items by type (Electrical, Plumbing, etc.)

#### Work Packages Tab

1. View list of work packages
2. Create new packages with "Create Package" button
3. Search and filter packages
4. Import packages from templates (currently unavailable - see Known Issues)
5. Download template for offline editing
6. View package details including:
   - Contained work items
   - Estimated hours
   - Required skill levels
   - Dependencies between items

*[SCREENSHOT: Work Packages tab with package list and create button]*

#### Work Items Tab

1. View list of standardized work items
2. Add new items with "Add Work Item" button
3. Filter by category and skill level
4. Search for specific items
5. View item details:
   - Estimated hours
   - Required skill level
   - Category

*[SCREENSHOT: Work Items tab showing filtering options and the item list with skill levels]*

#### Categories Tab

1. View and manage work item categories
2. Add new categories with "Add Category" button
3. Search existing categories
4. Reorder categories using up/down arrows
5. Edit category names and descriptions

*[SCREENSHOT: Categories tab showing the category management interface]*

### Technician Master List

1. Navigate to Technicians section from the sidebar
2. Use the Technician Master List to:
   - View all technicians with filtering by specialty, availability, and employment type
   - Check technician assignment status and current location
   - Review performance metrics and customer ratings
   - Compare cost efficiency across different employment types

#### Technician Details

1. Click on a technician to view their detailed profile:
   - Contact information (phone, WhatsApp, email)
   - Technical specialties and certifications
   - Current assignments
   - Employment details and cost information
   - Performance metrics and ratings

#### Employment Type Comparison

1. Navigate to the "Employment Comparison" tab
2. View comparative metrics by employment type:
   - Average cost per hour
   - Average cost per task
   - Customer satisfaction ratings
   - Completion rates
   - Punctuality rates
3. Filter by period (monthly, quarterly, yearly)
4. Export reports for resource planning

*[SCREENSHOT: Employment comparison dashboard showing cost metrics across different employment types]*

### Communication

1. Navigate to Communication section from the sidebar
2. Send internal messages
3. View conversation history
4. Use WhatsApp integration for customer communication
5. Access email templates

### Mobile Access

A responsive design allows for using the application on mobile devices:
- Simplified interface
- Touch-friendly controls
- Offline capabilities for field technicians

---

## Common Workflows

### New Project Setup

1. Create a new customer record
2. Create a new project
3. Assign team members
4. Create initial work orders
5. Upload relevant documents
6. Set up project timeline and milestones

### Work Order Lifecycle

1. Work order creation
2. Assignment to technician
3. Status updates (In Progress)
4. Document/photo uploads
5. Inventory allocation
6. Time tracking
7. Completion and sign-off
8. Billing generation

### Using Work Master for Work Orders

1. Select appropriate work package template
2. Assign to project
3. Adjust estimated hours if needed
4. Assign technicians based on required skill levels
5. Track progress against standardized estimates

### Inventory Management Workflow

1. Stock level monitoring
2. Reorder point notifications
3. Purchase order creation
4. Receiving inventory
5. Allocating inventory to work orders
6. Tracking usage

### Document Approval Workflow

1. Document upload
2. Routing for approval
3. Review and comments
4. Version control
5. Final approval
6. Distribution to relevant parties

### Technician Management Workflow

1. Add new technician with basic information
   - Employee number and contact details
   - Technical specialties
   - Employment type (employment contract, sub-contractor, self-employed)
2. Set up employment-specific details
   - For employment contract: monthly salary and benefits package
   - For sub-contractor: contract fee and payment terms
   - For self-employed: hourly rate and tax classification
3. Track performance metrics automatically
   - Record technician check-ins/check-outs
   - Monitor task completion rates
   - Collect customer ratings
4. Perform employment type cost comparison
   - Record cost metrics monthly
   - Generate KPI reports quarterly
   - Compare metrics across employment types
   - Use insights for resource allocation decisions

---

## Troubleshooting

### Common Issues

1. **Login Problems**
   - Verify your credentials
   - Use the password reset functionality
   - Contact admin if issues persist

2. **Performance Issues**
   - Close unused browser tabs
   - Clear browser cache
   - Check internet connection
   - Verify you're using a supported browser

3. **Data Not Saving**
   - Look for error messages
   - Check required fields
   - Try refreshing the page
   - Report to support if issue persists

4. **Mobile Access Issues**
   - Ensure you're using the latest app version
   - Check internet connection
   - Try switching between Wi-Fi and cellular data

5. **Work Master API Errors**
   - If you see "Failed to load" messages, check server connectivity
   - Verify API endpoints are correctly configured
   - Contact administrator if issues persist

6. **404 Errors in Action Columns**
   - Many modules may show 404 errors when clicking action buttons (Edit, Delete, View)
   - **Cause**: Missing route handlers or incorrect API endpoint configuration
   - **Temporary workaround**: 
     - For document viewing: Use the Documents section directly
     - For editing items: Use the main form interfaces
     - For critical actions: Contact your administrator
   - These issues will be addressed in the next application update

### Getting Help

1. **In-App Support**
   - Look for the help icon (?) in the top-right corner
   - Use the built-in feedback form
   - Check the knowledge base

2. **Administrator Support**
   - Contact your organization's system administrator
   - Email: support@fieldservicesapp.com
   - Phone: (555) 123-4567

---

## Known Issues and Limitations

### Current Development Status

This application is currently in active development. Some features may be incomplete or have limited functionality:

1. **Action Buttons in List Views**: 
   - Edit, Delete, and View detail actions in many modules currently return 404 errors
   - This affects Work Master, Documents, and other modules
   - Development team is actively working on fixing these routes

2. **API Connections**:
   - Some backend API endpoints may return 500 errors during development
   - Calendar and Work Master modules have client-side fallback data
   - Not all data is being saved to the database in the current version

3. **Work Master Template Functionality**:
   - **Import Button Issue**: The "Import" button in the Work Master section currently does not function properly
   - **Template Download Issue**: The template download may return a 404 error
   - **Root Cause**: The backend API endpoint implementations for importing work packages from templates are incomplete:
     - The `_import_from_csv`, `_import_from_excel`, and `_import_from_word` methods in the backend have placeholder implementations
     - The API route is configured but lacks full functionality
   - **Workaround**: Create work packages manually through the "Create Package" button
   - **Alternative**: Work with your administrator to enter data directly through the Django admin interface

4. **Documentation Placeholders**:
   - Screenshots mentioned in documentation with [SCREENSHOT] tags will be added in the final version
   - Some UI elements may differ slightly from those described

5. **Future Enhancements**:
   - Full integration with external APIs
   - Mobile app version
   - Enhanced reporting with PDF export
   - Offline data synchronization
   - Complete template import functionality for Work Master packages
