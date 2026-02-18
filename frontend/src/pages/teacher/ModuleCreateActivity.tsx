import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'
import teacherService, { type GeneratorJob } from '../../services/teacher.service'
import { toast } from '../../hooks/useToast'
import PageHeader from '../../components/ui/PageHeader'
import Spinner from '../../components/ui/Spinner'
import { Sparkles, Upload, CheckCircle2, Clock, AlertCircle, FileText, ArrowLeft } from 'lucide-react'

export default function ModuleCreateActivity() {
  const { moduleId } = useParams<{ moduleId: string }>()
  const { user } = useAuth()
  const navigate = useNavigate()
  
  const [file, setFile] = useState<File | null>(null)
  const [params, setParams] = useState({ topic: '', difficulty: 'medium', language: 'python' })
  const [uploading, setUploading] = useState(false)
  const [job, setJob] = useState<GeneratorJob | null>(null)
  const [polling, setPolling] = useState(false)

  const handleUploadAndGenerate = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!user || !file || !moduleId) return
    setUploading(true)
    try {
      const j = await teacherService.startGeneration(file, {
        teacher_id: user.id,
        topic: params.topic || undefined,
        difficulty: params.difficulty,
        language: params.language,
        module_id: moduleId,
      })
      setJob(j)
      toast({ title: 'Generación iniciada', variant: 'success' })
      // Start polling
      if (j.status === 'processing') {
        pollStatus(j.job_id)
      }
    } catch (error: any) {
      console.error('Error starting generation:', error)
      toast({ title: error?.response?.data?.detail || 'Error iniciando generación', variant: 'error' })
    } finally {
      setUploading(false)
    }
  }

  const pollStatus = async (jobId: string) => {
    setPolling(true)
    const interval = setInterval(async () => {
      try {
        const status = await teacherService.getGenerationStatus(jobId)
        setJob(status)
        if (status.status !== 'processing') {
          clearInterval(interval)
          setPolling(false)
          if (status.status === 'awaiting_approval') {
            try {
              const draft = await teacherService.getGenerationDraft(jobId)
              console.log('📋 Draft loaded:', {
                status: draft.status,
                exercises: draft.draft_exercises?.length,
                awaiting_approval: draft.awaiting_approval
              })
              setJob(draft)
            } catch (error: any) {
              console.error('Error fetching draft:', error)
              toast({ title: error?.response?.data?.detail || 'Error cargando ejercicios', variant: 'error' })
            }
          }
        }
      } catch (error: any) {
        console.error('Error polling status:', error)
        clearInterval(interval)
        setPolling(false)
      }
    }, 3000)
  }

  const handlePublish = async () => {
    if (!job || !moduleId) return
    
    console.log('🚀 Publishing exercises:', {
      job_id: job.job_id,
      activity_title: params.topic,
      module_id: moduleId,
      draft_exercises_count: job.draft_exercises?.length
    })
    
    try {
      const result = await teacherService.publishGeneration(job.job_id, {
        activity_title: params.topic || 'Actividad Generada',
        module_id: moduleId
      })
      
      console.log('✅ Publish result:', result)
      
      setJob(result)
      toast({ title: `Publicados ${result.exercise_count || 0} ejercicios`, variant: 'success' })
      
      // Redirect back to module after 2 seconds
      setTimeout(() => {
        navigate(`/teacher/modules/${moduleId}`)
      }, 2000)
    } catch (error: any) {
      console.error('❌ Error publishing:', error)
      console.error('Error details:', error?.response?.data)
      toast({ title: error?.response?.data?.detail || 'Error publicando', variant: 'error' })
    }
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title={
          <div className="flex items-center gap-3">
            <button 
              onClick={() => navigate(`/teacher/modules/${moduleId}`)} 
              className="rounded-lg p-2 hover:bg-gray-100 transition-colors"
            >
              <ArrowLeft className="h-5 w-5 text-gray-500" />
            </button>
            <span>Crear Actividad con IA</span>
          </div>
        }
        description="Sube un PDF con material didáctico y genera ejercicios automáticamente"
      />

      {/* Upload Form */}
      <div className="rounded-xl border border-gray-200 bg-white p-6">
        <form onSubmit={handleUploadAndGenerate} className="space-y-5">
          {/* File upload */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Material Didáctico (PDF) <span className="text-red-500">*</span>
            </label>
            <label className="flex flex-col items-center justify-center w-full h-40 border-2 border-dashed border-gray-200 rounded-lg cursor-pointer hover:bg-gray-50 hover:border-gray-300 transition-all">
              <div className="flex flex-col items-center">
                <Upload className="h-10 w-10 text-gray-300 mb-3" />
                <p className="text-sm font-medium text-gray-600">
                  {file ? file.name : 'Arrastrá o hacé clic para subir un PDF'}
                </p>
                {file && (
                  <div className="mt-2 flex items-center gap-2">
                    <CheckCircle2 className="h-4 w-4 text-green-500" />
                    <p className="text-xs text-gray-500">{(file.size / 1024 / 1024).toFixed(1)} MB</p>
                  </div>
                )}
                {!file && <p className="text-xs text-gray-400 mt-1">El contenido del PDF se usará para generar ejercicios relevantes</p>}
              </div>
              <input
                type="file"
                accept=".pdf"
                required
                className="hidden"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
              />
            </label>
          </div>

          {/* Params */}
          <div className="grid grid-cols-1 gap-5">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Título de la Actividad <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={params.topic}
                onChange={(e) => setParams({ ...params, topic: e.target.value })}
                required
                placeholder="Ej: Introducción a Programación Orientada a Objetos"
                className="flex h-11 w-full rounded-lg border border-gray-200 bg-white px-4 text-sm focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent"
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Dificultad</label>
                <select
                  value={params.difficulty}
                  disabled
                  className="flex h-11 w-full rounded-lg border border-gray-200 bg-gray-100 px-4 text-sm focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent cursor-not-allowed"
                >
                  <option value="medium">Medio</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Lenguaje</label>
                <select
                  value={params.language}
                  disabled
                  className="flex h-11 w-full rounded-lg border border-gray-200 bg-gray-100 px-4 text-sm focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent cursor-not-allowed"
                >
                  <option value="python">Python</option>
                </select>
              </div>
            </div>
          </div>

          <div className="pt-2">
            <button
              type="submit"
              disabled={!file || !params.topic || uploading}
              className="inline-flex items-center gap-2 rounded-lg bg-gray-900 px-6 py-3 text-sm font-medium text-white hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {uploading ? (
                <>
                  <Spinner size="sm" className="border-gray-600 border-t-white" />
                  Generando...
                </>
              ) : (
                <>
                  <Sparkles className="h-4 w-4" />
                  Generar Ejercicios con IA
                </>
              )}
            </button>
          </div>
        </form>
      </div>

      {/* Job Status */}
      {job && (
        <div className="rounded-xl border border-gray-100 bg-white p-6">
          <div className="flex items-center gap-3 mb-5">
            {job.status === 'processing' && <Clock className="h-6 w-6 text-blue-500 animate-spin" />}
            {job.status === 'awaiting_approval' && <AlertCircle className="h-6 w-6 text-amber-500" />}
            {job.status === 'completed' && <CheckCircle2 className="h-6 w-6 text-emerald-500" />}
            {job.status === 'error' && <AlertCircle className="h-6 w-6 text-red-500" />}
            {!['processing', 'awaiting_approval', 'completed', 'error'].includes(job.status) && <AlertCircle className="h-6 w-6 text-gray-400" />}
            <div className="flex-1">
              <h3 className="text-base font-semibold text-gray-900">
                {job.status === 'processing' ? 'Generando ejercicios con IA...' :
                 job.status === 'awaiting_approval' ? 'Ejercicios listos para revisión' :
                 job.status === 'completed' ? '¡Ejercicios publicados exitosamente!' :
                 job.status === 'error' ? 'Error en la generación' :
                 `Estado: ${job.status}`}
              </h3>
              <p className="text-xs text-gray-500 mt-0.5">
                {job.status === 'processing' ? 'Esto puede tomar unos minutos. Estamos analizando el PDF y generando ejercicios personalizados.' :
                 job.status === 'awaiting_approval' ? 'Revisa los ejercicios generados y publicalos cuando estés listo' :
                 job.status === 'completed' ? 'Los ejercicios ya están disponibles en el módulo' :
                 job.status === 'error' ? (job.error || 'Ocurrió un error inesperado') :
                 'Estado desconocido'}
              </p>
            </div>
          </div>

          {/* Draft exercises */}
          {job.draft_exercises && job.draft_exercises.length > 0 && (
            <div className="space-y-3">
              <div className="flex items-center justify-between mb-3">
                <h4 className="text-sm font-medium text-gray-700">Ejercicios Generados ({job.draft_exercises.length})</h4>
              </div>
              
              {job.draft_exercises.map((ex, idx) => (
                <div key={`draft-ex-${job.job_id}-${idx}`} className="rounded-lg border border-gray-100 bg-gray-50 p-4 hover:border-gray-200 transition-colors">
                  <div className="flex items-start gap-3">
                    <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-white border border-gray-200 shrink-0">
                      <FileText className="h-4 w-4 text-gray-500" />
                    </div>
                    <div className="flex-1">
                      <h5 className="text-sm font-semibold text-gray-900">{ex.title}</h5>
                      <p className="text-xs text-gray-600 mt-1 line-clamp-2">
                        {ex.description || ex.mission_markdown?.slice(0, 150) || 'Sin descripción'}
                      </p>
                      <div className="mt-2 flex items-center gap-3">
                        <span className="inline-flex items-center rounded-full bg-white border border-gray-200 px-2 py-0.5 text-[10px] font-medium text-gray-600 uppercase">
                          {ex.language}
                        </span>
                        <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-medium uppercase ${
                          ex.difficulty === 'easy' ? 'bg-green-50 text-green-700 border border-green-200' :
                          ex.difficulty === 'hard' ? 'bg-red-50 text-red-700 border border-red-200' :
                          'bg-yellow-50 text-yellow-700 border border-yellow-200'
                        }`}>
                          {ex.difficulty}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}

              {job.status === 'awaiting_approval' && (
                <div className="pt-3 flex gap-3">
                  <button
                    onClick={handlePublish}
                    className="inline-flex items-center gap-2 rounded-lg bg-gray-900 px-5 py-2.5 text-sm font-medium text-white hover:bg-gray-800 transition-colors"
                  >
                    <CheckCircle2 className="h-4 w-4" />
                    Aprobar y Publicar Actividad
                  </button>
                  <button
                    onClick={() => navigate(`/teacher/modules/${moduleId}`)}
                    className="rounded-lg px-4 py-2.5 text-sm font-medium text-gray-600 hover:bg-gray-100 transition-colors"
                  >
                    Cancelar
                  </button>
                </div>
              )}
            </div>
          )}

          {polling && (
            <div className="flex items-center gap-2 text-sm text-gray-500 mt-4 p-3 bg-blue-50 rounded-lg">
              <Spinner size="sm" className="border-blue-300 border-t-blue-600" />
              <span>Procesando con IA...</span>
            </div>
          )}

          {job.status === 'completed' && job.activity_id && (
            <div className="mt-4 p-4 bg-emerald-50 border border-emerald-200 rounded-lg">
              <div className="flex items-start gap-3">
                <CheckCircle2 className="h-5 w-5 text-emerald-600 mt-0.5" />
                <div>
                  <p className="text-sm font-medium text-emerald-900">
                    {job.exercise_count} ejercicios publicados exitosamente
                  </p>
                  <p className="text-xs text-emerald-700 mt-1">
                    Redirigiendo al módulo...
                  </p>
                </div>
              </div>
            </div>
          )}

          {job.status === 'error' && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
              <div className="flex items-start gap-3">
                <AlertCircle className="h-5 w-5 text-red-600 mt-0.5" />
                <div>
                  <p className="text-sm font-medium text-red-900">Error en la generación</p>
                  <p className="text-xs text-red-700 mt-1">{job.error || 'Ocurrió un error inesperado'}</p>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
