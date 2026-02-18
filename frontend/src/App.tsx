import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './contexts/AuthContext'

// Layouts
import StudentLayout from './layouts/StudentLayout'
import TeacherLayout from './layouts/TeacherLayout'

// Auth pages
import LoginPage from './pages/auth/LoginPage'
import RegisterPage from './pages/auth/RegisterPage'

// Student pages
import StudentDashboard from './pages/student/Dashboard'
import StudentCourses from './pages/student/Courses'
import StudentCourseDetail from './pages/student/CourseDetail'
import StudentActivities from './pages/student/Activities'
import StudentWorkspace from './pages/student/Workspace'
import StudentGrades from './pages/student/Grades'
import StudentTutor from './pages/student/Tutor'

// Teacher pages
import TeacherDashboard from './pages/teacher/Dashboard'
import TeacherActivities from './pages/teacher/Activities'
import TeacherActivityDetail from './pages/teacher/ActivityDetail'
import TeacherModules from './pages/teacher/Modules'
import TeacherModuleDetail from './pages/teacher/ModuleDetail'
import TeacherModuleCreateActivity from './pages/teacher/ModuleCreateActivity'
import TeacherModuleActivityAnalytics from './pages/teacher/ModuleActivityAnalytics'
import TeacherStudents from './pages/teacher/Students'
import TeacherAnalytics from './pages/teacher/Analytics'
import TeacherGenerator from './pages/teacher/Generator'

function ProtectedRoute({ children, role }: { children: React.ReactNode; role?: string }) {
  const { user, isLoading, isTeacher } = useAuth()

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-gray-300 border-t-gray-900" />
      </div>
    )
  }

  if (!user) return <Navigate to="/login" replace />

  if (role && !user.roles?.includes(role)) {
    // Redirect to appropriate dashboard based on user role
    const redirectPath = isTeacher ? '/teacher' : '/'
    return <Navigate to={redirectPath} replace />
  }

  return <>{children}</>
}

export default function App() {
  const { user, isTeacher } = useAuth()

  return (
    <Routes>
      {/* Public */}
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />

      {/* Student Routes */}
      <Route
        path="/"
        element={
          <ProtectedRoute role="student">
            <StudentLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<StudentDashboard />} />
        <Route path="courses" element={<StudentCourses />} />
        <Route path="courses/:courseId" element={<StudentCourseDetail />} />
        <Route path="activities" element={<StudentActivities />} />
        <Route path="activities/:activityId" element={<StudentWorkspace />} />
        <Route path="grades" element={<StudentGrades />} />
        <Route path="tutor/:activityId" element={<StudentTutor />} />
      </Route>

      {/* Teacher Routes */}
      <Route
        path="/teacher"
        element={
          <ProtectedRoute role="teacher">
            <TeacherLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<TeacherDashboard />} />
        <Route path="activities" element={<TeacherActivities />} />
        <Route path="activities/:activityId" element={<TeacherActivityDetail />} />
        <Route path="modules" element={<TeacherModules />} />
        <Route path="modules/:moduleId" element={<TeacherModuleDetail />} />
        <Route path="modules/:moduleId/create-activity" element={<TeacherModuleCreateActivity />} />
        <Route path="modules/:moduleId/activities/:activityId" element={<TeacherModuleActivityAnalytics />} />
        <Route path="students" element={<TeacherStudents />} />
        <Route path="analytics" element={<TeacherAnalytics />} />
        <Route path="generator" element={<TeacherGenerator />} />
      </Route>

      {/* Catch all - redirect to appropriate dashboard or login */}
      <Route 
        path="*" 
        element={
          <Navigate 
            to={user ? (isTeacher ? '/teacher' : '/') : '/login'} 
            replace 
          />
        } 
      />
    </Routes>
  )
}
