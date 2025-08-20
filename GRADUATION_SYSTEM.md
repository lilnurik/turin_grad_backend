# Student Graduation System

This document describes the new student graduation system implemented in Turin Grad Hub.

## Overview

The graduation system manages student status transitions from "current student" to "graduate" based on academic years that run from June to June.

## New Database Fields

### Student Status and Degree Information
- `student_status`: ENUM('current', 'graduate') - Default: 'current'
- `degree_level`: ENUM('bachelor', 'master', 'phd', 'dsc') - Default: 'bachelor'  
- `student_type`: ENUM('regular', 'free_applicant', 'external') - Default: 'regular'

## Academic Year System

Academic years run from June to June:
- Example: "06.2021-06.2025" means June 2021 to June 2025
- Students become eligible for graduation starting June of their graduation year
- Current academic year calculation considers the June cutoff

## API Endpoints

### Admin Graduation Management

#### Get Graduating Students
```http
GET /api/admin/graduating-students
```
Returns students eligible for graduation based on current academic year.

Query Parameters:
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 10)
- `faculty`: Filter by faculty
- `degreeLevel`: Filter by degree level (bachelor, master, phd, dsc)

#### Confirm Graduation
```http
POST /api/admin/students/{student_id}/confirm-graduation
```
Changes student status from 'current' to 'graduate'. Creates activity log and notification.

#### Revert Graduation
```http
POST /api/admin/students/{student_id}/revert-graduation
```
Changes student status from 'graduate' back to 'current'. Creates activity log and notification.

#### Update Graduation Information
```http
PUT /api/admin/students/{student_id}/graduation-info
```
Updates student admission year, graduation year, degree level, and other graduation-related information.

Request Body:
```json
{
  "admissionYear": 2021,
  "graduationYear": 2025,
  "degreeLevel": "bachelor",
  "studentType": "regular",
  "faculty": "Факультет информатики",
  "direction": "Программная инженерия"
}
```

#### Get Graduation Statistics
```http
GET /api/admin/graduation-statistics
```
Returns comprehensive statistics about students and graduates.

Query Parameters:
- `year`: Filter by graduation year (default: current academic year)

### Student Filtering

#### Filter Students by Status
```http
GET /api/students?studentStatus=current
GET /api/students?studentStatus=graduate
```

#### Filter Students by Degree Level
```http
GET /api/students?degreeLevel=bachelor
GET /api/students?degreeLevel=master
GET /api/students?degreeLevel=phd
GET /api/students?degreeLevel=dsc
```

## Degree Levels and Types

### Bachelor's Degree
- Duration: 4-5 years
- Student Type: Always 'regular'

### Master's Degree  
- Duration: 2-3 years
- Student Type: Always 'regular'

### PhD (Doctor of Philosophy)
- Duration: 3-5 years
- Student Types:
  - `regular`: Standard PhD student
  - `free_applicant`: PhD student not bound to specific supervisor initially
  - `external`: External PhD candidate

### DSc (Doctor of Science)
- Duration: 3-4 years
- Student Types: Same as PhD

## Validation Rules

The system enforces the following validation rules:

1. **Duration Validation**: Graduation year must be appropriate for the degree level
2. **Student Type Validation**: Bachelor and Master students must be 'regular' type
3. **Graduation Eligibility**: Students can only graduate if current date >= June of graduation year
4. **Status Consistency**: Graduated students cannot be modified without explicit permission

## User Model Methods

### `is_eligible_for_graduation()`
Checks if a student is eligible for graduation based on:
- Must be a student
- Must have graduation year set
- Must not already be graduated  
- Current date must be >= June of graduation year

### `get_academic_year_period()`
Returns formatted academic year period string (e.g., "06.2021-06.2025")

### `validate_graduation_data()`
Validates graduation-related data consistency and returns list of validation errors.

## Sample Data

The system includes sample data with different student types:
- Bachelor students (current and graduate)
- Master's students
- PhD students (regular and free applicant)
- Students from different faculties
- Students with different graduation years

## Activity Logging

All graduation-related actions are logged:
- `STUDENT_GRADUATED`: When admin confirms graduation
- `STUDENT_GRADUATION_REVERTED`: When admin reverts graduation
- `STUDENT_GRADUATION_INFO_UPDATED`: When graduation info is updated

## Notifications

Students receive notifications for:
- Graduation confirmation
- Graduation status reversion
- Graduation information updates

## Testing

Run the test script to see the system in action:
```bash
python3 test_graduation_system.py
```

This script demonstrates:
- Academic year calculations
- Graduation eligibility checks
- Data validation
- Statistics generation
- Available API endpoints