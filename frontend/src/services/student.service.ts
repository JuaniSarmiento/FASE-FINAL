import api from './api'
import { ActivitySummaryDTO, TutorMessageDTO, SubjectDTO, CourseDTO } from '../types/dtos'

// --- Restored Interfaces for UI Compatibility ---

export interface TestCase {
  test_number: number
  description: string
  input_data: string
  expected_output: string
  is_hidden: boolean
}

export interface Exercise {
  exercise_id?: string
  id?: string // For compatibility with backend
  title: string
  difficulty: string
  mission_markdown?: string
  problem_statement?: string // For compatibility with backend
  starter_code: string
  language: string
  order_index?: number
  total_exercises?: number
  solution_code?: string
  test_cases?: TestCase[]
  description?: string
}

export interface Activity extends ActivitySummaryDTO {
  activity_id: string
  type?: string
  created_at?: string
  course_id?: string
  starter_code?: string
  current_code?: string
  submission_status?: string
  instructions?: string
  grade?: number
  max_grade?: number
    module_title?: string
}

export interface Workspace {
  activity_id: string
  activity_title: string
  instructions: string
  starter_code: string
  template_code?: string
  tutor_context?: string
  language: string
  difficulty: string
  estimated_time_minutes: number
}

export interface SubmissionRequest {
  code: string
  is_final_submission?: boolean
  exercise_id?: string
  all_exercise_codes?: { [exercise_id: string]: string }
}

export interface SubmissionResponse {
  submission_id: string
  status: string
  message: string
  feedback?: string
  grade?: number
  ai_feedback?: string
  next_exercise_id?: string
  is_activity_complete?: boolean
  exercises_details?: unknown[]
  details?: any
}

export interface ChatRequest {
  message: string
  current_code?: string
  error_context?: string
}

export interface ChatResponse {
  response: string
  rag_context_used: boolean
  context_snippets?: string[]
  cognitive_phase?: string
  hint_level?: number
}

export interface SessionResponse {
  session_id: string
  status: string
  // Extend as needed
}

export interface DashboardData {
  personal_data: unknown
  stats: unknown
  gamification: unknown
}

export interface Course {
  course_id: string
  name: string
  year: number
  semester: number
  modules: any[]
}

export interface ActivityHistory {
  activity_id: string
  activity_title: string
  course_id: string
  status: string
  grade: number
  cognitive_phase: string
  completion_percentage: number
}

export interface Grade {
  grade_id: string
  activity_id: string
  grade: number
  activity_title: string
  passed: boolean
  course_name?: string
  max_grade?: number
  teacher_feedback?: string
}

export interface GradesSummary {
  average_grade: number
  total_activities: number
  passed_activities: number
  graded_activities: number
  highest_grade: number
  lowest_grade: number
}

export interface Gamification {
  xp: number
  level: number
  streak_days: number
}

export interface StudentExerciseResult {
  exercise_id: string
  exercise_title: string
  grade: number
  ai_feedback: string
  passed: boolean
}

export interface StudentActivityResults {
  exercises: StudentExerciseResult[]
}

// --- Service Implementation ---

const studentService = {
  // ... (dashboard methods)
  // DEPRECATED: Dashboard data should be fetched individually
  async getDashboard(studentId: string): Promise<DashboardData> {
    // Return empty/default structure as we move to real data
    return {
      personal_data: { name: "Student" },
      stats: { completed: 0, distinct: 0 },
      gamification: { points: 0, level: 1 }
    }
  },

  // ... (courses)
  async getCourses(studentId: string): Promise<Course[]> {
    const res = await api.get('/student/courses', { params: { student_id: studentId } })
    return res.data
  },

  async joinCourse(studentId: string, accessCode: string) {
    return { success: true }
  },

  // ... (activities)
  async getActivities(studentId: string): Promise<Activity[]> {
    const res = await api.get('/student/activities', { params: { student_id: studentId } })
    return res.data.map((d: any) => ({
      ...d,
      activity_id: d.id,
      status: d.status || 'PENDING',
      instructions: d.description
    }))
  },

  async getActivity(activityId: string, studentId: string): Promise<Activity> {
    return {
      id: activityId,
      activity_id: activityId,
      title: "Activity " + activityId,
      description: "Desc",
      difficulty: "EASY",
      status: "PENDING",
      instructions: "Instructions..."
    } as Activity
  },

  async getExercises(activityId: string, studentId: string): Promise<Exercise[]> {
    const res = await api.get(`/student/activities/${activityId}`)
    // Map backend ActivityDetailsDTO excercises to frontend Exercise interface
    return res.data.exercises.map((ex: any) => ({
      exercise_id: ex.exercise_id,
      id: ex.exercise_id,
      title: ex.title,
      difficulty: ex.difficulty,
      problem_statement: ex.problem_statement,
      starter_code: ex.starter_code || "# Escribe tu código aquí, sin funciones\nprint(f\"Hola {nombre}\")",
      language: ex.language,
      order_index: ex.order,
      test_cases: []
    }))
  },

  async getWorkspace(activityId: string, studentId: string): Promise<Workspace> {
    // REFACTOR: Now fetching real data from getActivityDetails endpoint
    const res = await api.get(`/student/activities/${activityId}`)
    const data = res.data
    const hasExercises = data.exercises && data.exercises.length > 0

    // Fallback logic for instructions if not present in exercise
    let instructions = data.description || "Instrucciones de la actividad..."
    if (hasExercises && data.exercises[0].problem_statement) {
      instructions = data.exercises[0].problem_statement
    }

    return {
      activity_id: data.activity_id,
      activity_title: data.title,
      instructions: instructions,
      starter_code: hasExercises ? (data.exercises[0].starter_code || "") : "",
      language: "python", // defaulting to python for MVP
      difficulty: data.difficulty || "intermediate",
      estimated_time_minutes: 30, // Mocked for now or add to backend model
      template_code: hasExercises ? data.exercises[0].template_code : ""
    }
  },

  async getActivityHistory(studentId: string): Promise<ActivityHistory[]> {
    return []
  },

  // Sessions
  async startSession(data: { student_id: string; activity_id: string; mode?: string }) {
    const res = await api.post('/student/sessions', data)
    return res.data
  },

  async getSessionDetails(sessionId: string): Promise<any> {
    const res = await api.get(`/student/sessions/${sessionId}`)
    return res.data
  },

  async sendSessionMessage(sessionId: string, data: { message: string, current_code?: string }): Promise<ChatResponse> {
    // Backend expects SendMessageRequest: { session_id, message, code_context }
    const payload = {
      session_id: sessionId, // Required by DTO
      message: data.message,
      code_context: data.current_code // Map to backend field
    }
    const res = await api.post(`/student/sessions/${sessionId}/chat`, payload)

    return {
      response: res.data.content,
      rag_context_used: false
    }
  },

  async submitSessionCode(sessionId: string, data: { code: string; is_final_submission?: boolean; exercise_id?: string; all_exercise_codes?: any }): Promise<SubmissionResponse> {
    const res = await api.post(`/student/sessions/${sessionId}/submit`, data)
    return {
      submission_id: "temp", // Backend doesn't return ID yet
      status: res.data.passed ? "passed" : "failed",
      message: res.data.feedback,
      feedback: res.data.feedback, // Add feedback alias
      grade: res.data.grade,
      passed: res.data.passed,
      details: res.data.details
    } as SubmissionResponse
  },

  async chatWithTutor(activityId: string, studentId: string, data: ChatRequest) {
    try {
      const res = await api.post(`/learning/activities/${activityId}/chat`, { query: data.message })
      return {
        response: res.data.response,
        rag_context_used: true
      }
    } catch (e) {
      console.error("Chat error", e)
      return { response: "Error connecting to AI Tutor.", rag_context_used: false }
    }
  },

  async getGrades(studentId: string, activityId?: string): Promise<Grade[]> {
    const res = await api.get('/student/grades', { params: { student_id: studentId } })
    return res.data
  },

  async getGradesSummary(studentId: string): Promise<GradesSummary> {
    return {
      average_grade: 0,
      total_activities: 0,
      passed_activities: 0,
      graded_activities: 0,
      highest_grade: 0,
      lowest_grade: 0
    }
  },

  async getGamification(studentId: string): Promise<Gamification> {
    return { xp: 0, level: 1, streak_days: 0 }
  },

  async getActivityAttempt(activityId: string, studentId: string) {
    return { final_grade: null, submitted_at: null }
  },

  async getActivityResults(activityId: string, studentId: string): Promise<StudentActivityResults> {
    return { exercises: [] }
  }
}

export default studentService
