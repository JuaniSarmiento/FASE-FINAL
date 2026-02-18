import api from './api'
import { TeacherDashboardDTO, StudentRiskDTO, IncidentDTO } from '../types/dtos'
import type { Activity, Exercise } from './student.service'

// --- Restored Interfaces for UI Compatibility ---

export interface CreateActivityRequest {
  title: string
  course_id: string
  teacher_id: string
  instructions?: string
  policy?: string
  max_ai_help_level?: number
}

export interface GenerateExerciseRequest {
  topic: string
  difficulty: string
  unit_number?: number
  language?: string
  concepts?: string[]
  estimated_time_minutes?: number
  count?: number
}

export interface StudentInfo {
  user_id: string
  username: string
  email: string
  full_name: string
}

export interface GeneratorJob {
  job_id: string
  status: string
  awaiting_approval?: boolean
  draft_exercises?: Exercise[]
  error?: string
  activity_id?: string
  exercise_count?: number
}

export interface ModuleCreate {
  title: string
  description?: string
  order_index?: number
  is_published?: boolean
}

export interface ModuleResponse {
  module_id: string
  title: string
  description: string
  course_id: string
  order_index: number
  is_published: boolean
}

export interface ModuleStats {
  active_students: number
  total_activities: number
  total_submissions: number
  average_grade: number
}

export interface ModuleActivity {
  activity_id: string
  title: string
  status: string
  total_submissions: number
  graded_submissions: number
  exercise_count?: number
}

export interface ModuleStudent {
  user_id: string
  full_name: string
  email: string
  role: string
  status: string
}

export interface ActivityStudentProgress {
  student_id: string
  email: string
  total_exercises: number
  submitted_exercises: number
  avg_score: number
  progress_percentage: number
}

export interface StudentSubmissionDetail {
  exercise_id: string
  exercise_title: string
  code: string
  score: number
  feedback: string
  submitted_at: string
}

export interface GradeSubmissionRequest {
  grade: number;
  feedback?: string;
  override_ai?: boolean;
}

export interface TeacherCourse {
  course_id: string
  course_name: string
  semester: string
}

export interface TeacherModule {
  module_id: string
  name: string
  description: string
  course_id: string
  student_count: number
}

// ==================== AI ANALYTICS TYPES ====================

export interface AIInteractionSummary {
  student_id: string
  student_name: string
  total_interactions: number
  copy_seeking_count: number
  conceptual_questions_count: number
  logical_questions_count: number
  avg_frustration: number
  avg_understanding: number
  last_interaction: string | null
}

export interface AIChat {
  interaction_id: string
  exercise_title: string | null
  student_message: string
  ai_response: string
  interaction_type: string
  question_quality: string | null
  cognitive_phase: string | null
  shows_effort: boolean
  gave_direct_answer: boolean
  created_at: string
}

export interface StudentRiskAnalysis {
  analysis_id: string
  student_id: string
  student_name: string
  risk_score: number
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'
  diagnosis: string
  evidence: string[]
  intervention: string
  confidence_score: number
  ai_abuse_detected: boolean
  shows_learning_effort: boolean
  copy_paste_pattern: boolean
  total_ai_interactions: number
  copy_seeking_count: number
  conceptual_questions_count: number
  created_at: string
}

export interface StudentActivityAttemptSummary {
  status: string | null
  final_grade: number | null
  submitted_at: string | null
  ai_feedback: string | null
}

export interface StudentExerciseResult {
  exercise_id: string
  exercise_title: string
  grade: number
  ai_feedback: string
  passed: boolean
  submitted_at: string | null
}

export interface StudentActivityResults {
  attempt: StudentActivityAttemptSummary
  exercises: StudentExerciseResult[]
  total_exercises: number
  passed_exercises: number
}

// --- Service Interface ---

export interface TeacherService {
  getDashboard(): Promise<TeacherDashboardDTO>
  getStudents(): Promise<StudentInfo[]>
  getActivities(teacherId: string, limit?: number): Promise<Activity[]>
  getActivity(activityId: string): Promise<Activity>
  deleteActivity(activityId: string): Promise<void>
  publishActivity(activityId: string): Promise<{ success: boolean }>
  updateActivityStatus(activityId: string, status: string): Promise<{ success: boolean }>
  getActivityAnalytics(activityId: string): Promise<{ total_students: number; submitted_count: number; average_grade: number; difficulty_rating: string; avg_time_minutes: number; interaction_count: number }>
  getIncidents(): Promise<IncidentDTO[]>
  reportIncident(data: any): Promise<any>
  getCourses(teacherId: string): Promise<TeacherCourse[]>
  getModules(teacherId: string): Promise<TeacherModule[]>
  createModule(name: string, teacherId: string, description?: string): Promise<any>
  updateModule(moduleId: string, data: any): Promise<any>
  deleteModule(moduleId: string): Promise<void>
  getModuleStats(moduleId: string): Promise<ModuleStats>
  getModuleActivities(moduleId: string): Promise<ModuleActivity[]>
  getModuleStudents(moduleId: string): Promise<ModuleStudent[]>
  addStudentsToModule(moduleId: string, studentIds: string[]): Promise<void>
  removeStudentFromModule(moduleId: string, studentId: string): Promise<void>
  createActivity(data: CreateActivityRequest): Promise<any>
  generateExercise(activityId: string, data: GenerateExerciseRequest): Promise<any>
  getExercises(activityId: string): Promise<Exercise[]>
  startGeneration(file: File, params: any): Promise<{ job_id: string; status: string }>
  getGenerationStatus(jobId: string): Promise<GeneratorJob>
  approveAndPublish(activityId: string, exercises: any[]): Promise<{ success: boolean }>
  getStudentRiskHistory(studentId: string): Promise<any[]>
  getStudentActivityResults(studentId: string, activityId: string): Promise<StudentActivityResults>
  getStudentActivityDetails(activityId: string, studentId: string): Promise<any>
  getStudentAIChats(studentId: string, activityId: string): Promise<{ chats: AIChat[]; total: number }>
  generateRiskAnalysis(studentId: string, activityId: string): Promise<StudentRiskAnalysis>
  getGenerationDraft(jobId: string): Promise<GeneratorJob>
  publishGeneration(jobId: string, data: any): Promise<GeneratorJob>
  getActivityStudents(activityId: string): Promise<ActivityStudentProgress[]>
  getActivityStudentProgress(activityId: string): Promise<ActivityStudentProgress[]>
  uploadDocument(activityId: string, file: File): Promise<void>
  getTeacherAlerts(): Promise<{ alerts: any[] }>
  getCourseAnalytics(courseId: string): Promise<any>
}

// --- Service Implementation ---

const teacherService: TeacherService = {
  // Dashboard
  async getDashboard(): Promise<TeacherDashboardDTO> {
    const res = await api.get('/teacher/dashboard')
    // Ensure return type matches
    return {
      ...res.data,
      personal_data: res.data.personal_data || { name: "Teacher" },
      stats: res.data.stats || { active_students: 0, average_attendance: 0, average_grade: 0, total_students: 0 },
      top_students: res.data.top_students || [],
      recent_activity: res.data.recent_activity || []
    }
  },

  // Students & Risk
  async getStudents(): Promise<StudentInfo[]> {
    const res = await api.get('/teacher/students')
    return res.data.map((s: StudentRiskDTO) => ({
      user_id: s.student_id,
      email: s.email,
      full_name: s.full_name,
      username: s.email.split('@')[0],
      risk_level: s.risk_level,
      average_grade: s.average_grade
    }))
  },

  async getActivities(teacherId: string, limit?: number) {
    const res = await api.get('/teacher/activities')
    return res.data
  },

  async getActivity(activityId: string) {
    const res = await api.get(`/teacher/activities/${activityId}`)
    const a = res.data
    return {
      id: a.id,
      activity_id: a.id,
      title: a.title,
      status: a.status,
      description: a.description,
      instructions: a.description, // Map description to instructions for UI compatibility
      type: a.type,
      created_at: a.created_at,
      // Default others
      difficulty: "medium",
      topic: "General"
    } as unknown as Activity
  },

  async deleteActivity(activityId: string) {
    return
  },

  async publishActivity(activityId: string, courseId?: string) {
    const res = await api.post(`/teacher/activities/${activityId}/publish`, {
      course_id: courseId
    })
    return res.data
  },

  async updateActivityStatus(activityId: string, status: string) {
    const res = await api.patch(`/teacher/activities/${activityId}/status`, { status })
    return res.data
  },

  async getActivityAnalytics(activityId: string) {
    return {
      total_students: 0,
      submitted_count: 0,
      average_grade: 0,
      difficulty_rating: "medium",
      avg_time_minutes: 0,
      interaction_count: 0
    }
  },

  // Governance / Incidents
  async getIncidents(): Promise<IncidentDTO[]> {
    const res = await api.get('/governance/incidents')
    return res.data
  },

  async reportIncident(data: any) {
    const res = await api.post('/governance/incidents', data)
    return res.data
  },

  // Courses & Modules
  async getCourses(teacherId: string): Promise<TeacherCourse[]> {
    const res = await api.get('/academic/courses')
    return res.data.map((c: any) => ({
      course_id: c.id,
      course_name: c.name,
      semester: c.semester || "1",
    }))
  },

  async getModules(teacherId: string): Promise<TeacherModule[]> {
    const res = await api.get('/teacher/activities')
    const activities: Activity[] = res.data
    console.log('Fetched activities for modules:', activities)
    return activities
      .filter(a => a.type?.toLowerCase() === 'module')
      .map(a => ({
        module_id: a.activity_id || a.id,
        name: a.title,
        description: a.description || "",
        course_id: a.course_id || "default_course",
        student_count: 0
      }))
  },

  async createModule(name: string, teacherId: string, description?: string) {
    console.log('Creating module as activity:', name)
    const res = await api.post('/teacher/activities', {
      title: name,
      description: description || "",
      course_id: "default_course",
      teacher_id: teacherId,
      type: "module"
    })
    const activity = res.data
    return {
      module_id: activity.id,
      name: activity.title,
      description: activity.description,
      course_id: activity.course_id,
      student_count: 0
    }
  },

  async updateModule(moduleId: string, data: any) {
    return {}
  },

  async deleteModule(moduleId: string) {
    return
  },

  async getModuleStats(moduleId: string): Promise<ModuleStats> {
    return { active_students: 0, total_activities: 0, total_submissions: 0, average_grade: 0 }
  },

  async getModuleActivities(moduleId: string): Promise<ModuleActivity[]> {
    console.log(`[TeacherService] Fetching activities for module ${moduleId}`);
    try {
      const res = await api.get(`/teacher/modules/${moduleId}/activities`);
      return res.data.map((a: any) => ({
        activity_id: a.id,
        title: a.title,
        status: a.status,
        total_submissions: 0, // Mock for now
        graded_submissions: 0, // Mock for now
        exercise_count: a.exercise_count || 0 // Use real count from backend
      }));
    } catch (error) {
      console.error(`[TeacherService] Error fetching module activities:`, error);
      return [];
    }
  },

  async getModuleStudents(moduleId: string): Promise<ModuleStudent[]> {
    const res = await api.get(`/teacher/modules/${moduleId}/students`)
    return res.data
  },

  async addStudentsToModule(moduleId: string, studentIds: string[]) {
    await api.post(`/teacher/modules/${moduleId}/students`, { student_ids: studentIds })
  },

  async uploadDocument(activityId: string, file: File) {
    const formData = new FormData()
    formData.append('file', file)
    await api.post(`/learning/activities/${activityId}/document`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  async removeStudentFromModule(moduleId: string, studentId: string) {
    await api.delete(`/teacher/modules/${moduleId}/students/${studentId}`)
  },

  // Activity Creation
  async createActivity(data: CreateActivityRequest) {
    const res = await api.post('/teacher/activities', data)
    return res.data
  },

  async generateExercise(activityId: string, data: GenerateExerciseRequest) {
    const res = await api.post('/learning/generate', {
      activity_id: activityId,
      ...data
    })
    return res.data
  },

  async getExercises(activityId: string) {
    console.log(`[TeacherService] Fetching exercises for activity ${activityId}`);
    try {
      const res = await api.get(`/teacher/activities/${activityId}/exercises`);
      console.log(`[TeacherService] Fetched ${res.data.length} exercises`);
      return res.data;
    } catch (error) {
      console.error(`[TeacherService] Error fetching exercises for ${activityId}:`, error);
      return [];
    }
  },

  async startGeneration(file: File, params: any) {
    console.log("Starting Real RAG Generation...", params);

    // 1. Create Activity (Draft)
    // We map params to CreateActivityRequest. 
    // We assume params contains title, and we default course/teacher if needed.
    const activityData: CreateActivityRequest = {
      title: params.title || params.topic || "AI Generated Activity",
      // CRITICAL FIX: Ensure course_id is set to module_id if available.
      course_id: params.module_id || params.course_id || "default_course",
      teacher_id: params.teacher_id || "current_user",
      instructions: "Generated by AI",
      policy: "strict"
    };

    console.log("Creating Activity with Data:", activityData);

    let activity;
    try {
      activity = await this.createActivity(activityData);
      console.log("Activity Created:", activity.id);
    } catch (e) {
      console.error("Error creating activity:", e);
      throw e;
    }

    // 2. Upload Document
    if (file) {
      try {
        console.log("Uploading Document:", file.name);
        await this.uploadDocument(activity.id, file);
      } catch (e) {
        console.error("Error uploading document:", e);
        // We continue? If upload fails, RAG won't work but basic generation might.
        // Let's throw to warn user.
        throw e;
      }
    }

    // 3. Generate Exercises
    try {
      console.log("Triggering AI Generation...");
      await this.generateExercise(activity.id, {
        topic: params.topic || params.title, // Use title as topic
        difficulty: params.difficulty || "medium",
        language: params.language || "python",
        unit_number: 1,
        count: 5,
        concepts: []
      });
    } catch (e) {
      console.error("Error generating exercises:", e);
      throw e;
    }

    // 4. Return "completed" with activity ID as job ID
    // Since we awaited everything, it is done.
    return { job_id: activity.id, status: "completed" };
  },

  async getGenerationStatus(jobId: string) {
    // jobId is activityId in our implementation
    try {
      const exercises = await this.getExercises(jobId);
      return {
        job_id: jobId,
        status: "completed",
        draft_exercises: exercises,
        exercise_count: exercises.length
      }
    } catch (e) {
      console.error("Error fetching generation status:", e);
      // Return empty or error state
      return { job_id: jobId, status: "error", error: "Failed to fetch exercises" }
    }
  },

  async getGenerationDraft(jobId: string) {
    // Re-use status logic
    return this.getGenerationStatus(jobId);
  },

  async publishGeneration(jobId: string, data: any) {
    // Publish the activity
    console.log(`Publishing generation ${jobId} with data:`, data);
    await this.publishActivity(jobId);

    // Check if we need to update the course_id if it was wrong?
    // The backend publish command essentially just flips the status.

    let count = 5;
    try {
      const exercises = await this.getExercises(jobId);
      count = exercises.length;
    } catch (e) {
      console.warn("Could not fetch exercise count for publish return");
    }
    return { job_id: jobId, status: "completed", exercise_count: count }
  },

  async approveAndPublish(activityId: string, exercises: any[]) {
    // Just publish
    // We don't have module_id here easily unless passed. 
    // But publishGeneration is the main one used by RAG flow.
    await this.publishActivity(activityId);
    return { success: true }
  },

  async getStudentRiskHistory(studentId: string) {
    return []
  },

  async getStudentActivityResults(studentId: string, activityId: string): Promise<StudentActivityResults> {
    return {
      total_exercises: 0,
      passed_exercises: 0,
      attempt: { status: null, final_grade: null, submitted_at: null, ai_feedback: null },
      exercises: []
    }
  },

  async getActivityStudents(activityId: string): Promise<ActivityStudentProgress[]> {
    const res = await api.get(`/teacher/activities/${activityId}/students`)
    return res.data
  },

  async getActivityStudentProgress(activityId: string): Promise<ActivityStudentProgress[]> {
    return this.getActivityStudents(activityId)
  },

  async getStudentAIChats(studentId: string, activityId: string) {
    return { chats: [], total: 0 }
  },

  async getStudentActivityDetails(activityId: string, studentId: string) {
    const res = await api.get(`/teacher/activities/${activityId}/students/${studentId}/details`)
    return res.data
  },

  async generateRiskAnalysis(studentId: string, activityId: string) {
    const res = await api.post(`/teacher/activities/${activityId}/students/${studentId}/analyze`, {})
    return res.data
  },



  async getTeacherAlerts() {
    return { alerts: [] }
  },

  async getCourseAnalytics(courseId: string) {
    return {
      total_students: 0,
      average_risk_score: 0,
      students_at_risk: 0,
      completion_rate: 0,
      student_profiles: []
    }
  }
}

export default teacherService
