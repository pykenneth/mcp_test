# Technician Master List

The Technician Master List module provides comprehensive management of field technicians, including their personal details, specialties, employment information, and performance metrics. The system supports comparing different employment types (employment contract, sub-contractor, and self-employed) for cost evaluation.

## Table of Contents

- [Models Overview](#models-overview)
- [Technician Model](#technician-model)
- [Specialty Model](#specialty-model)
- [Certification Model](#certification-model)
- [Cost Metrics and KPI Models](#cost-metrics-and-kpi-models)
- [API Endpoints](#api-endpoints)
- [Using the Employment Type Comparison](#using-the-employment-type-comparison)

## Models Overview

The Technician Master List consists of the following key models:

- **Technician**: Core model storing technician details
- **Specialty**: Represents a technical skill or area of expertise
- **Certification**: Records professional certifications and qualifications
- **TechnicianCertification**: Tracks certifications held by technicians with expiry dates
- **TechnicianLocation**: Records GPS locations during field work
- **TechnicianCheckIn**: Logs check-in/check-out events at work sites
- **TechnicianRating**: Stores customer ratings and feedback
- **TechnicianCostMetrics**: Tracks cost-related performance metrics
- **EmploymentTypeKpiReport**: Aggregates KPIs by employment type for comparison

## Technician Model

The Technician model is the core entity that stores information about field technicians.

### Fields

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| employee_number | CharField | Unique identifier for the technician | Yes |
| full_name | CharField | Complete name of the technician | Yes |
| nickname | CharField | Informal name or alias | No |
| phone_number | PhoneNumberField | Primary contact number | Yes |
| whatsapp_number | PhoneNumberField | WhatsApp contact number | No |
| email | EmailField | Email address | No |
| profile_image | ImageField | Photo of the technician | No |
| emergency_contact | CharField | Emergency contact information | No |
| hire_date | DateField | When the technician was hired | No |
| job_title | CharField | Official position/title | No |
| specialties | ManyToManyField | Technical skills and expertise areas | No |
| availability_status | CharField | Current working status (available, on_assignment, on_leave, inactive) | Yes |
| customer_rating | FloatField | Average rating from customers (0-5) | Auto-calculated |
| punctuality_rate | FloatField | Percentage of on-time arrivals | Auto-calculated |
| completion_rate | FloatField | Percentage of tasks completed successfully | Auto-calculated |

### Employment Information Fields

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| employment_type | CharField | Type of employment relationship | Yes |
| hourly_rate | DecimalField | Hourly cost rate | Depends on employment type |
| monthly_salary | DecimalField | Monthly salary (for employment contract) | For employment contract |
| contract_fee | DecimalField | Fee per contract (for sub-contractors) | For sub-contractors |
| tax_classification | CharField | Tax classification | For self-employed |
| payment_terms | CharField | Payment terms | No |
| benefits_package | TextField | Description of benefits | For employment contract |

### Editing Instructions

- When creating new technicians, the `employee_number` must be unique
- For employment contract technicians, fill in `monthly_salary` and `benefits_package`
- For sub-contractors, provide `contract_fee` and `payment_terms` 
- For self-employed technicians, include `hourly_rate` and `tax_classification`
- Performance metrics (customer_rating, punctuality_rate, completion_rate) are automatically calculated and should not be manually set

## Specialty Model

The Specialty model represents a technical skill or area of expertise.

### Fields

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| name | CharField | Name of the specialty | Yes |
| description | TextField | Detailed description | No |
| category | CharField | Grouping category | No |

### Editing Instructions

- Create specialties before assigning them to technicians
- Group related specialties using the `category` field for easier filtering
- Consistent naming helps with reporting and assignment

## Certification Model

The Certification model represents professional certifications and qualifications.

### Fields

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| name | CharField | Name of the certification | Yes |
| issuing_organization | CharField | Organization that issues the certification | Yes |
| description | TextField | Details about the certification | No |
| validity_period | PositiveIntegerField | Validity period in months | No |

### TechnicianCertification Model

This model connects technicians to their certifications with issue and expiry dates.

### Fields

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| technician | ForeignKey | Reference to the technician | Yes |
| certification | ForeignKey | Reference to the certification | Yes |
| issue_date | DateField | When the certification was issued | Yes |
| expiry_date | DateField | When the certification expires | No |
| certificate_number | CharField | Unique identifier for this certificate | No |

### Editing Instructions

- When adding a certification to a technician, the expiry date can be automatically calculated if the certification has a validity_period
- Set up reminders for expiring certifications to ensure compliance
- Each technician can have multiple certifications

## Cost Metrics and KPI Models

These models track cost-related performance metrics and enable comparison between different employment types.

### TechnicianCostMetrics Model

Records cost metrics for individual technicians over a specific period.

### Fields

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| technician | ForeignKey | Reference to the technician | Yes |
| period_start | DateField | Start of the measurement period | Yes |
| period_end | DateField | End of the measurement period | Yes |
| total_hours_worked | DecimalField | Total hours worked in the period | Yes |
| total_tasks_completed | PositiveIntegerField | Number of tasks completed | Yes |
| total_cost | DecimalField | Total cost for the technician in this period | Yes |
| cost_per_hour | DecimalField | Calculated cost per hour | Auto-calculated |
| cost_per_task | DecimalField | Calculated cost per task | Auto-calculated |
| efficiency_score | FloatField | Overall efficiency score (0-100) | Auto-calculated |
| notes | TextField | Additional context or comments | No |

### EmploymentTypeKpiReport Model

Aggregates KPIs by employment type for comparative analysis.

### Fields

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| period_type | CharField | Type of period (monthly, quarterly, yearly) | Yes |
| period_start | DateField | Start of the reporting period | Yes |
| period_end | DateField | End of the reporting period | Yes |
| employment_type | CharField | Type of employment relationship | Yes |
| technicians_count | PositiveIntegerField | Number of technicians included | Auto-calculated |
| avg_cost_per_hour | DecimalField | Average cost per hour | Auto-calculated |
| avg_cost_per_task | DecimalField | Average cost per task | Auto-calculated |
| avg_customer_rating | FloatField | Average customer satisfaction | Auto-calculated |
| avg_completion_rate | FloatField | Average task completion rate | Auto-calculated |
| avg_punctuality_rate | FloatField | Average punctuality rate | Auto-calculated |
| avg_efficiency_score | FloatField | Average efficiency score | Auto-calculated |
| total_cost | DecimalField | Total cost for this employment type | Auto-calculated |
| total_tasks_completed | PositiveIntegerField | Total tasks completed | Auto-calculated |

### Editing Instructions

- Cost metrics are entered manually using the record_metrics API endpoint
- KPI reports are generated automatically using the employment-kpi/generate API endpoint
- Don't modify auto-calculated fields directly; they're derived from raw metrics

## Role-Based Permissions

Access to the Technician Master List is controlled through role-based permissions:

### Admin Users
- Full access to all features and data
- Can create, read, update, and delete all records
- Access to employment type comparison and cost metrics
- Can generate KPI reports

### Managers
- Can create and update technician records
- Cannot delete technician records (reserved for admins)
- Can view all technicians and their metrics
- Can access employment type comparison data
- Can record cost metrics and generate reports

### Technicians
- Can view their own profile only
- Can update limited fields in their own profile
- Cannot view other technicians' data
- Can view their own performance metrics and cost records
- Cannot access employment type comparison data

### Regular Users
- Limited view access based on assigned functions
- Cannot modify data
- No access to sensitive cost information

## API Endpoints

### Technician Endpoints

- `GET /api/v1/technicians/` - List technicians (filtered by role permissions)
- `POST /api/v1/technicians/` - Create a new technician (Admin/Manager only)
- `GET /api/v1/technicians/{id}/` - Get technician details (own profile or Admin/Manager)
- `PUT/PATCH /api/v1/technicians/{id}/` - Update technician (own profile or Admin/Manager)
- `DELETE /api/v1/technicians/{id}/` - Delete technician (Admin only)
- `GET /api/v1/technicians/available/` - List available technicians
- `GET /api/v1/technicians/{id}/assignments/` - Get technician's assignments
- `GET /api/v1/technicians/{id}/performance/` - Get performance metrics
- `POST /api/v1/technicians/{id}/check-in/` - Record check-in
- `POST /api/v1/technicians/{id}/check-out/` - Record check-out
- `GET /api/v1/technicians/team-performance/` - Get team-wide metrics

### Specialty and Certification Endpoints

- `GET /api/v1/specialties/` - List all specialties
- `GET /api/v1/certifications/` - List all certifications

### Cost Metrics and KPI Endpoints

- `GET /api/v1/cost-metrics/` - List all cost metrics
- `GET /api/v1/cost-metrics/by-technician/?technician_id={id}` - Get metrics for a specific technician
- `POST /api/v1/cost-metrics/record-metrics/` - Record new cost metrics
- `GET /api/v1/employment-kpi/` - List all employment type KPI reports
- `POST /api/v1/employment-kpi/generate/` - Generate new KPI reports
- `GET /api/v1/employment-kpi/compare/` - Compare KPIs by employment type

## Using the Employment Type Comparison

The system provides tools to compare the cost-effectiveness of different employment types:

1. **Record Cost Metrics**: For each technician, record cost metrics regularly (monthly recommended)
   ```
   POST /api/v1/cost-metrics/record-metrics/
   {
     "technician_id": 1,
     "period_start": "2025-04-01",
     "period_end": "2025-04-30",
     "total_hours_worked": 168,
     "total_tasks_completed": 42,
     "total_cost": 5500
   }
   ```

2. **Generate KPI Reports**: Periodically generate comparison reports
   ```
   POST /api/v1/employment-kpi/generate/
   {
     "period_type": "monthly",
     "period_start": "2025-04-01",
     "period_end": "2025-04-30"
   }
   ```

3. **Compare Employment Types**: Review comparative metrics to make staffing decisions
   ```
   GET /api/v1/employment-kpi/compare/?period_type=monthly&period_start=2025-04-01&period_end=2025-04-30
   ```

The comparison will show which employment type delivers the best balance of cost, quality (customer ratings), and efficiency for different types of work.
