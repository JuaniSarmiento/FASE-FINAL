export interface UserDTO {
    id: string;
    email: string;
    username: string;
    full_name: string;
    roles: string[];
    is_active: boolean;
    is_verified: boolean;
}

export interface AuthResponseDTO {
    access_token: string;
    token_type: string;
    user: UserDTO;
}

export interface ActivitySummaryDTO {
    id: string;
    title: string;
    description: string;
    difficulty: string;
    status: string;
}

export interface TeacherDashboardDTO {
    total_students: number;
    total_activities: number;
    active_students: number;
    recent_activities: any[]; // Define stricter if needed
}

export interface StudentRiskDTO {
    student_id: string;
    email: string;
    full_name: string;
    risk_level: string;
    average_grade: number;
    last_active: string;
}

export interface IncidentDTO {
    id: string;
    student_id: string;
    incident_type: string;
    description: string;
    severity: string;
    status: string;
    created_at: string;
    resolved_at?: string;
    resolution_notes?: string;
}

export interface SubjectDTO {
    id: string;
    name: string;
    code: string;
}

export interface CourseDTO {
    id: string;
    subject_id: string;
    year: number;
    semester: number;
}

export interface EnrollmentDTO {
    id: string;
    student_id: string;
    course_id: string;
    status: string;
}

export interface TutorMessageDTO {
    role: string;
    content: string;
    timestamp: string;
}

export interface SubmitSolutionResponse {
    submission_id: string;
    status: string;
    grade: number;
    feedback: string;
    passed: boolean;
}
