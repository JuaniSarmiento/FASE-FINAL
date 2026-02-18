import { useEffect, useState } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'
import teacherService, { type ActivityStudentProgress } from '../../services/teacher.service'
import type { Activity, Exercise } from '../../services/student.service'
import { toast } from '../../hooks/useToast'
import PageHeader from '../../components/ui/PageHeader'
import Spinner from '../../components/ui/Spinner'
import {
  ArrowLeft,
  Users,
  FileCode,
  Upload,
  Sparkles,
  Share2,
  BarChart3,
  Clock,
  X,
  BrainCircuit,
  Smartphone,
  CheckCircle,
  AlertTriangle
} from 'lucide-react'
import EmptyState from '../../components/ui/EmptyState'

export default function TeacherActivityDetail() {
  const { activityId } = useParams<{ activityId: string }>()
  const navigate = useNavigate()
  const { user } = useAuth()
  const [activity, setActivity] = useState<Activity | null>(null)
  const [exercises, setExercises] = useState<Exercise[]>([])
  const [students, setStudents] = useState<ActivityStudentProgress[]>([])
  const [stats, setStats] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [genForm, setGenForm] = useState({ topic: '', difficulty: 'medium', language: 'python' })
  const [showGenerate, setShowGenerate] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [togglingStatus, setTogglingStatus] = useState(false)

  // Inspection Modal State
  const [selectedStudent, setSelectedStudent] = useState<string | null>(null)
  const [studentDetails, setStudentDetails] = useState<any>(null)
  const [riskAnalysis, setRiskAnalysis] = useState<any>(null)
  const [analyzingRisk, setAnalyzingRisk] = useState(false)

  useEffect(() => {
    if (!activityId) return
    Promise.all([
      teacherService.getActivity(activityId).catch(() => null),
      teacherService.getExercises(activityId).catch(() => []),
      teacherService.getActivityStudents(activityId).catch(() => []),
    ])
      .then(([a, e, s]) => {
        setActivity(a);
        setExercises(e);
        setStudents(s);

        if (s) {
          const submitted = s.filter(std => std.submitted_exercises > 0).length
          const total = s.length
          const avg = submitted > 0
            ? s.reduce((acc, std) => acc + (std.avg_score || 0), 0) / submitted
            : 0
          setStats({
            submitted_count: submitted,
            total_students: total,
            average_score: avg
          })
        }
      })
      .catch(() => toast({ title: 'Error cargando actividad', variant: 'error' }))
      .finally(() => setLoading(false))
  }, [activityId])

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!activityId || !genForm.topic) return
    setGenerating(true)
    try {
      const ex = await teacherService.generateExercise(activityId, {
        topic: genForm.topic,
        difficulty: genForm.difficulty,
        language: genForm.language,
      })
      setExercises((prev) => [...prev, ex])
      toast({ title: 'Ejercicio generado con IA', variant: 'success' })
      setGenForm({ topic: '', difficulty: 'medium', language: 'python' })
      setShowGenerate(false)
    } catch {
      toast({ title: 'Error generando ejercicio', variant: 'error' })
    } finally {
      setGenerating(false)
    }
  }

  const handleUpload = async (file: File) => {
    if (!activityId) return
    setUploading(true)
    try {
      await teacherService.uploadDocument(activityId, file)
      toast({ title: 'Documento subido y procesado para RAG', variant: 'success' })
    } catch {
      toast({ title: 'Error subiendo documento', variant: 'error' })
    } finally {
      setUploading(false)
    }
  }

  const toggleStatus = async () => {
    if (!activity) return
    setTogglingStatus(true)
    const newStatus = activity.status === 'published' ? 'draft' : 'published'
    try {
      await teacherService.updateActivityStatus(activity.id, newStatus)
      setActivity({ ...activity, status: newStatus })
      toast({ title: `Actividad ${newStatus === 'published' ? 'publicada' : 'oculta'}`, variant: 'success' })
    } catch {
      toast({ title: 'Error actualizando estado', variant: 'error' })
    } finally {
      setTogglingStatus(false)
    }
  }

  const handleInspectStudent = async (studentId: string) => {
    setSelectedStudent(studentId)
    setStudentDetails(null)
    setRiskAnalysis(null)
    try {
      const details = await teacherService.getStudentActivityDetails(activityId!, studentId)
      setStudentDetails(details)
      if (details.risk_analysis) {
        setRiskAnalysis(details.risk_analysis)
      }
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
    } catch (e) {
      toast({ title: 'Error cargando detalles', variant: 'error' })
    }
  }


  if (loading) {
    return <div className="flex items-center justify-center py-20"><Spinner size="lg" /></div>
  }

  if (!activity) {
    return <p className="text-center text-gray-500 py-20">Actividad no encontrada</p>
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button onClick={() => navigate('/teacher/modules')} className="p-2 hover:bg-gray-100 rounded-full transition-colors">
            <ArrowLeft className="w-6 h-6 text-gray-700" />
          </button>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{activity?.title}</h1>
            <p className="text-gray-500">Módulo: {activity?.module_title}</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          {/* Status Badge */}
          <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-sm font-medium border ${activity?.status === 'published'
            ? 'bg-green-50 text-green-700 border-green-200'
            : 'bg-yellow-50 text-yellow-700 border-yellow-200'
            }`}>
            <span className={`w-2 h-2 rounded-full ${activity?.status === 'published' ? 'bg-green-500' : 'bg-yellow-500'}`} />
            {activity?.status === 'published' ? 'Publicado' : 'Borrador'}
          </span>

          {/* Publish Toggle Button */}
          <button
            onClick={toggleStatus}
            disabled={togglingStatus}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${activity?.status === 'published'
              ? 'bg-white border border-gray-300 text-gray-700 hover:bg-gray-50'
              : 'bg-black text-white hover:bg-gray-800'
              }`}
          >
            {togglingStatus ? 'Actualizando...' : (activity?.status === 'published' ? 'Ocultar' : 'Publicar')}
          </button>

          <button className="p-2 hover:bg-gray-100 rounded-lg text-gray-500">
            <Share2 className="h-5 w-5" />
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Stats Section - Left Column */}
        <div className="lg:col-span-2 space-y-6">
          <div className="grid grid-cols-3 gap-4">
            <div className="p-4 rounded-xl border border-gray-100 bg-white">
              <div className="flex items-center gap-3 mb-2">
                <div className="p-2 rounded-lg bg-blue-50 text-blue-600">
                  <Users className="h-5 w-5" />
                </div>
                <span className="text-sm font-medium text-gray-500">Entregas</span>
              </div>
              <p className="text-2xl font-bold text-gray-900">
                {stats?.submitted_count || 0}/{stats?.total_students || 0}
              </p>
            </div>

            <div className="p-4 rounded-xl border border-gray-100 bg-white">
              <div className="flex items-center gap-3 mb-2">
                <div className="p-2 rounded-lg bg-green-50 text-green-600">
                  <BarChart3 className="h-5 w-5" />
                </div>
                <span className="text-sm font-medium text-gray-500">Promedio</span>
              </div>
              <p className="text-2xl font-bold text-gray-900">
                {stats?.average_score ? stats.average_score.toFixed(1) : '—'}
              </p>
            </div>

            <div className="p-4 rounded-xl border border-gray-100 bg-white">
              <div className="flex items-center gap-3 mb-2">
                <div className="p-2 rounded-lg bg-purple-50 text-purple-600">
                  <Clock className="h-5 w-5" />
                </div>
                <span className="text-sm font-medium text-gray-500">Tiempo Promedio</span>
              </div>
              <p className="text-2xl font-bold text-gray-900">45m</p>
            </div>
          </div>

          {/* Activity Description */}
          <div className="p-6 rounded-xl border border-gray-100 bg-white">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Descripción</h2>
            <p className="text-gray-600 leading-relaxed">
              {activity?.instructions || "Sin descripción."}
            </p>
          </div>

          {/* Exercises */}
          <div className="rounded-xl border border-gray-100 bg-white">
            <div className="flex items-center gap-2 p-5 pb-3">
              <FileCode className="h-4 w-4 text-gray-400" />
              <h2 className="text-sm font-semibold text-gray-900">Ejercicios ({exercises.length})</h2>
            </div>
            <div className="border-t border-gray-50 divide-y divide-gray-50">
              {exercises.length === 0 ? (
                <p className="p-5 text-center text-sm text-gray-400">No hay ejercicios. Genera uno con IA.</p>
              ) : (
                exercises.map((ex, idx) => (
                  <div key={ex.exercise_id} className="px-5 py-4">
                    <div className="flex items-center justify-between">
                      <h4 className="text-sm font-medium text-gray-900">
                        {idx + 1}. {ex.title}
                      </h4>
                      <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-medium ${ex.difficulty === 'easy' ? 'bg-emerald-50 text-emerald-700' :
                        ex.difficulty === 'medium' ? 'bg-amber-50 text-amber-700' :
                          'bg-red-50 text-red-700'
                        }`}>
                        {ex.difficulty}
                      </span>
                    </div>
                    {ex.problem_statement && (
                      <p className="mt-1 text-xs text-gray-500 line-clamp-2">{ex.problem_statement}</p>
                    )}
                    <div className="mt-2 flex items-center gap-2 text-[10px] text-gray-400">
                      <span className="uppercase">{ex.language || 'python'}</span>
                      {ex.test_cases && (
                        <>
                          <span>·</span>
                          <span>{ex.test_cases.length} tests</span>
                        </>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Generate Form */}
          <div className="flex gap-4">
            <button
              onClick={() => setShowGenerate(!showGenerate)}
              className="inline-flex items-center gap-2 rounded-lg bg-gray-900 px-4 py-2.5 text-sm font-medium text-white hover:bg-gray-800 transition-colors"
            >
              <Sparkles className="h-4 w-4" />
              Generating Exercise
            </button>
            <label className="inline-flex items-center gap-2 rounded-lg border border-gray-200 px-4 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50 cursor-pointer transition-colors">
              <Upload className="h-4 w-4" />
              {uploading ? 'Subiendo...' : 'Subir PDF'}
              <input
                type="file"
                accept=".pdf"
                className="hidden"
                onChange={(e) => e.target.files?.[0] && handleUpload(e.target.files[0])}
              />
            </label>
          </div>

          {showGenerate && (
            <div className="rounded-xl border border-gray-200 bg-white p-6">
              <h3 className="text-sm font-semibold text-gray-900 mb-4">Generar Ejercicio con IA</h3>
              <form onSubmit={handleGenerate} className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">Tema</label>
                  <input
                    type="text"
                    value={genForm.topic}
                    onChange={(e) => setGenForm({ ...genForm, topic: e.target.value })}
                    required
                    placeholder="Ej: Recursión"
                    className="flex h-10 w-full rounded-lg border border-gray-200 bg-white px-3 text-sm focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">Dificultad</label>
                  <select
                    value={genForm.difficulty}
                    onChange={(e) => setGenForm({ ...genForm, difficulty: e.target.value })}
                    className="flex h-10 w-full rounded-lg border border-gray-200 bg-white px-3 text-sm focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent"
                  >
                    <option value="easy">Fácil</option>
                    <option value="medium">Medio</option>
                    <option value="hard">Difícil</option>
                  </select>
                </div>
                <div className="flex items-end">
                  <button
                    type="submit"
                    disabled={generating}
                    className="inline-flex items-center gap-2 rounded-lg bg-gray-900 px-4 py-2.5 text-sm font-medium text-white hover:bg-gray-800 disabled:opacity-50 transition-colors"
                  >
                    {generating ? <Spinner size="sm" className="border-gray-600 border-t-white" /> : <Sparkles className="h-4 w-4" />}
                    Generar
                  </button>
                </div>
              </form>
            </div>
          )}
        </div>

        {/* Students List - Right Column */}
        <div className="rounded-xl border border-gray-100 bg-white h-fit">
          <div className="flex items-center justify-between p-5 border-b border-gray-50">
            <div className="flex items-center gap-2">
              <Users className="h-4 w-4 text-gray-400" />
              <h2 className="text-sm font-semibold text-gray-900">Estudiantes ({students.length})</h2>
            </div>
          </div>

          <div className="divide-y divide-gray-50 max-h-[600px] overflow-y-auto">
            {students.length === 0 ? (
              <p className="p-8 text-center text-sm text-gray-400">No hay entregas aún</p>
            ) : (
              students.map((s) => (
                <div
                  key={s.student_id}
                  className="flex items-center justify-between px-5 py-4 hover:bg-gray-50 transition-colors cursor-pointer group"
                  onClick={() => handleInspectStudent(s.student_id)}
                >
                  <div>
                    <p className="text-sm font-medium text-gray-900 group-hover:text-blue-600 transition-colors">{s.email}</p>
                    <div className="flex items-center gap-2 mt-1">
                      <span className="text-xs text-gray-500">
                        {s.submitted_exercises}/{s.total_exercises} ejercicios
                      </span>
                      {s.avg_score && (
                        <span className={`text-[10px] px-1.5 py-0.5 rounded font-medium ${s.avg_score >= 6 ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                          }`}>
                          {s.avg_score >= 6 ? 'Aprobado' : 'Riesgo'}
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="flex flex-col items-end gap-1">
                    <p className="text-sm font-bold text-gray-900">
                      {s.avg_score ? `${s.avg_score.toFixed(1)}` : '—'}
                      <span className="text-gray-400 text-xs font-normal">/10</span>
                    </p>
                    <span className="text-xs text-blue-600 font-medium opacity-0 group-hover:opacity-100 transition-opacity">
                      Ver Análisis
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Inspection Modal */}
      {selectedStudent && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 backdrop-blur-sm animate-in fade-in">
          <div className="w-full max-w-5xl max-h-[90vh] overflow-y-auto bg-white rounded-xl shadow-2xl p-0 flex flex-col">

            {/* Modal Header */}
            <div className="flex justify-between items-center px-6 py-4 border-b border-gray-100 sticky top-0 bg-white z-10">
              <div>
                <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
                  Inspección Completa
                  <span className="px-2 py-0.5 bg-gray-100 text-gray-600 rounded text-xs font-normal">Beta</span>
                </h2>
                <p className="text-sm text-gray-500 mt-0.5">
                  Estudiante: <span className="font-medium text-gray-900">{students.find(s => s.student_id === selectedStudent)?.email}</span>
                </p>
              </div>
              <button
                onClick={() => setSelectedStudent(null)}
                className="p-2 hover:bg-gray-100 rounded-lg text-gray-500 hover:text-gray-700 transition-colors"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            {/* Modal Content */}
            <div className="p-6">
              {studentDetails ? (
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

                  {/* Left Column: AI Analysis & Chat */}
                  <div className="space-y-6">
                    {/* Risk Analysis Card */}
                    <div className="bg-gradient-to-br from-gray-900 to-gray-800 p-5 rounded-xl text-white shadow-lg relative overflow-hidden">
                      <div className="absolute top-0 right-0 p-3 opacity-10">
                        <BrainCircuit className="h-24 w-24" />
                      </div>

                      <h3 className="font-semibold text-white/90 flex items-center gap-2 mb-4 relative z-10">
                        <BrainCircuit className="h-4 w-4 text-blue-400" />
                        Análisis de Riesgo IA
                      </h3>

                      {!riskAnalysis ? (
                        <div className="text-center py-6 relative z-10">
                          <div className="flex justify-center mb-4">
                            <div className="relative">
                              <div className="absolute inset-0 bg-blue-500 blur-xl opacity-20 animate-pulse"></div>
                              <BrainCircuit className="h-12 w-12 text-blue-400 relative z-10 animate-pulse" />
                            </div>
                          </div>
                          <p className="text-sm font-medium text-white mb-2">
                            Analizando perfil del estudiante...
                          </p>
                          <p className="text-xs text-gray-400 max-w-[80%] mx-auto leading-relaxed">
                            El análisis se está generando en background. Por favor, recarga la página en unos segundos.
                          </p>
                        </div>
                      ) : (
                        <div className="space-y-4 relative z-10 animate-in fade-in slide-in-from-bottom-2">
                          <div className={`p-3 rounded-lg border ${riskAnalysis.risk_level === 'HIGH' || riskAnalysis.risk_level === 'CRITICAL' ? 'bg-red-500/20 border-red-500/30 text-red-100' :
                            riskAnalysis.risk_level === 'MEDIUM' ? 'bg-yellow-500/20 border-yellow-500/30 text-yellow-100' :
                              'bg-green-500/20 border-green-500/30 text-green-100'
                            }`}>
                            <div className="text-[10px] font-bold uppercase tracking-wider mb-1 opacity-70">Nivel de Riesgo Detectado</div>
                            <div className="text-2xl font-bold flex items-center gap-2">
                              {riskAnalysis.risk_level}
                              <span className="text-sm font-normal opacity-70">({riskAnalysis.risk_score}%)</span>
                            </div>
                          </div>

                          <div>
                            <p className="text-[10px] font-bold text-gray-400 uppercase mb-1">Diagnóstico</p>
                            <p className="text-sm text-gray-200 italic leading-snug">"{riskAnalysis.diagnosis}"</p>
                          </div>

                          <div>
                            <p className="text-[10px] font-bold text-gray-400 uppercase mb-1">Consejo para el Docente</p>
                            <div className="text-xs text-gray-300 bg-white/5 p-3 rounded border border-white/10 leading-relaxed">
                              {riskAnalysis.teacher_advice}
                            </div>
                          </div>
                        </div>
                      )}
                    </div>

                    {/* Chat History Snippet */}
                    <div className="bg-white p-0 rounded-xl border border-gray-200 shadow-sm overflow-hidden">
                      <div className="px-4 py-3 border-b border-gray-100 bg-gray-50 flex justify-between items-center">
                        <h3 className="font-semibold text-gray-900 text-sm">Historial de Chat</h3>
                        <span className="text-xs text-gray-500 bg-white px-2 py-0.5 rounded border border-gray-200">
                          {studentDetails.chat_history?.length || 0} mensajes
                        </span>
                      </div>

                      <div className="max-h-[300px] overflow-y-auto p-4 space-y-3 bg-gray-50/50">
                        {(!studentDetails.chat_history || studentDetails.chat_history.length === 0) ? (
                          <div className="text-center py-8">
                            <Smartphone className="h-8 w-8 text-gray-300 mx-auto mb-2" />
                            <p className="text-gray-400 italic text-xs">No hay interacciones registradas.</p>
                          </div>
                        ) : (
                          studentDetails.chat_history.map((msg: any, i: number) => {
                            const isStudent = msg.role === 'user'
                            const displayRole = isStudent ? 'Estudiante' : 'Tutor IA'
                            return (
                              <div key={i} className={`flex flex-col max-w-[90%] ${isStudent ? 'ml-auto items-end' : 'mr-auto items-start'}`}>
                                <div className={`px-3 py-2 rounded-lg text-xs leading-relaxed shadow-sm ${isStudent
                                  ? 'bg-blue-600 text-white rounded-br-none'
                                  : 'bg-white border border-gray-200 text-gray-700 rounded-bl-none'
                                  }`}>
                                  {msg.content}
                                </div>
                                <span className="text-[10px] text-gray-400 mt-1 px-1">
                                  {displayRole} • {new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                </span>
                              </div>
                            )
                          })
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Right Column: Submission Details */}
                  <div className="lg:col-span-2 space-y-6">
                    <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm">
                      <div className="flex items-center justify-between mb-6">
                        <div>
                          <h3 className="font-bold text-gray-900 text-lg">Resultados de Evaluación</h3>
                          <p className="text-sm text-gray-500">Detalle ejercicio por ejercicio tal cual lo ve el alumno</p>
                        </div>
                        <div className="text-right">
                          <div className="text-sm text-gray-500 mb-1">Nota Final</div>
                          <div className="text-3xl font-bold text-gray-900">{studentDetails.final_grade}/100</div>
                        </div>
                      </div>

                      {(!studentDetails.exercises || studentDetails.exercises.length === 0) ? (
                        <EmptyState title="Sin entrega" description="El alumno no ha entregado esta actividad." icon={<FileCode className="h-10 w-10" />} />
                      ) : (
                        <div className="space-y-4">
                          {studentDetails.exercises.map((ex: any, i: number) => (
                            <div key={i} className="group">
                              <div className={`p-5 rounded-xl border transition-all ${ex.passed
                                ? 'border-green-100 bg-green-50/20 hover:border-green-200 hover:shadow-sm'
                                : 'border-red-100 bg-red-50/20 hover:border-red-200 hover:shadow-sm'
                                }`}>
                                <div className="flex justify-between items-start mb-3">
                                  <div className="flex items-center gap-3">
                                    <div className={`p-2 rounded-full ${ex.passed ? 'bg-green-100 text-green-600' : 'bg-red-100 text-red-600'}`}>
                                      {ex.passed ? <CheckCircle className="h-4 w-4" /> : <AlertTriangle className="h-4 w-4" />}
                                    </div>
                                    <div>
                                      <h4 className="font-semibold text-gray-900">{ex.title || `Ejercicio ${i + 1}`}</h4>
                                      <p className="text-xs text-gray-500">ID: {ex.exercise_id}</p>
                                    </div>
                                  </div>
                                  <span className={`px-3 py-1 rounded-full text-xs font-bold ${ex.passed ? 'bg-white text-green-700 border border-green-100' : 'bg-white text-red-700 border border-red-100'
                                    }`}>
                                    {ex.passed ? 'APROBADO' : 'FALLIDO'}
                                  </span>
                                </div>

                                <div className="pl-12">
                                  <div className="text-sm text-gray-700 bg-white p-4 rounded-lg border border-gray-100 shadow-sm leading-relaxed">
                                    <span className="font-bold text-xs text-gray-400 uppercase block mb-2 tracking-wider">Feedback del Tutor IA</span>
                                    {ex.feedback}
                                  </div>
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>

                </div>
              ) : (
                <div className="py-24 flex flex-col items-center justify-center text-center">
                  <Spinner size="lg" className="mb-4" />
                  <p className="text-gray-500">Cargando detalles del estudiante...</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
