import { useState } from 'react'
import { useAuth } from '../../contexts/AuthContext'
import teacherService, { type GeneratorJob } from '../../services/teacher.service'
import { toast } from '../../hooks/useToast'
import PageHeader from '../../components/ui/PageHeader'
import Spinner from '../../components/ui/Spinner'
import { Sparkles, Upload, CheckCircle2, Clock, AlertCircle, FileText } from 'lucide-react'

export default function TeacherGenerator() {
  const { user } = useAuth()
  const [file, setFile] = useState<File | null>(null)
  const [params, setParams] = useState({ topic: '', difficulty: 'medium', language: 'python', course_id: '' })
  const [uploading, setUploading] = useState(false)
  const [job, setJob] = useState<GeneratorJob | null>(null)
  const [polling, setPolling] = useState(false)

  const handleUploadAndGenerate = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!user || !file) return
    setUploading(true)
    try {
      const j = await teacherService.startGeneration(file, {
        teacher_id: user.id,
        topic: params.topic || undefined,
        difficulty: params.difficulty,
        language: params.language,
        course_id: params.course_id || undefined,
      })
      setJob(j)
      toast({ title: 'Generación iniciada', variant: 'success' })
      // Start polling
      if (j.status === 'processing') {
        pollStatus(j.job_id)
      }
    } catch {
      toast({ title: 'Error iniciando generación', variant: 'error' })
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
            const draft = await teacherService.getGenerationDraft(jobId)
            setJob(draft)
          }
        }
      } catch {
        clearInterval(interval)
        setPolling(false)
      }
    }, 3000)
  }

  const handlePublish = async () => {
    if (!job) return
    try {
      const result = await teacherService.publishGeneration(job.job_id, {
        activity_title: params.topic || 'Actividad Generada',
      })
      setJob(result)
      toast({ title: `Publicados ${result.exercise_count || 0} ejercicios`, variant: 'success' })
    } catch {
      toast({ title: 'Error publicando', variant: 'error' })
    }
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Generador de Ejercicios con IA"
        description="Sube un PDF con material didáctico y genera ejercicios automáticamente usando RAG"
      />

      {/* Upload Form */}
      <div className="rounded-xl border border-gray-200 bg-white p-6">
        <form onSubmit={handleUploadAndGenerate} className="space-y-5">
          {/* File upload */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Material Didáctico (PDF)</label>
            <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-dashed border-gray-200 rounded-lg cursor-pointer hover:bg-gray-50 transition-colors">
              <div className="flex flex-col items-center">
                <Upload className="h-8 w-8 text-gray-300 mb-2" />
                <p className="text-sm text-gray-500">
                  {file ? file.name : 'Arrastrá o hacé clic para subir un PDF'}
                </p>
                {file && <p className="text-xs text-gray-400 mt-0.5">{(file.size / 1024 / 1024).toFixed(1)} MB</p>}
              </div>
              <input
                type="file"
                accept=".pdf"
                className="hidden"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
              />
            </label>
          </div>

          {/* Params */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Tema</label>
              <input
                type="text"
                value={params.topic}
                onChange={(e) => setParams({ ...params, topic: e.target.value })}
                placeholder="Ej: Programación orientada a objetos"
                className="flex h-10 w-full rounded-lg border border-gray-200 bg-white px-3 text-sm focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Dificultad</label>
              <select
                value={params.difficulty}
                onChange={(e) => setParams({ ...params, difficulty: e.target.value })}
                className="flex h-10 w-full rounded-lg border border-gray-200 bg-white px-3 text-sm focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent"
              >
                <option value="easy">Fácil</option>
                <option value="medium">Medio</option>
                <option value="hard">Difícil</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Lenguaje</label>
              <select
                value={params.language}
                onChange={(e) => setParams({ ...params, language: e.target.value })}
                className="flex h-10 w-full rounded-lg border border-gray-200 bg-white px-3 text-sm focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent"
              >
                <option value="python">Python</option>
                <option value="javascript">JavaScript</option>
                <option value="java">Java</option>
                <option value="c">C</option>
              </select>
            </div>
          </div>

          <button
            type="submit"
            disabled={!file || uploading}
            className="inline-flex items-center gap-2 rounded-lg bg-gray-900 px-5 py-2.5 text-sm font-medium text-white hover:bg-gray-800 disabled:opacity-50 transition-colors"
          >
            {uploading ? (
              <Spinner size="sm" className="border-gray-600 border-t-white" />
            ) : (
              <Sparkles className="h-4 w-4" />
            )}
            Generar Ejercicios
          </button>
        </form>
      </div>

      {/* Job Status */}
      {job && (
        <div className="rounded-xl border border-gray-100 bg-white p-6">
          <div className="flex items-center gap-3 mb-4">
            {job.status === 'processing' && <Clock className="h-5 w-5 text-blue-500 animate-spin" />}
            {job.status === 'awaiting_approval' && <AlertCircle className="h-5 w-5 text-amber-500" />}
            {job.status === 'completed' && <CheckCircle2 className="h-5 w-5 text-emerald-500" />}
            {job.status === 'error' && <AlertCircle className="h-5 w-5 text-red-500" />}
            <div>
              <h3 className="text-sm font-semibold text-gray-900">
                {job.status === 'processing' ? 'Generando ejercicios...' :
                 job.status === 'awaiting_approval' ? 'Ejercicios listos para revisión' :
                 job.status === 'completed' ? 'Ejercicios publicados' :
                 'Error en la generación'}
              </h3>
              <p className="text-xs text-gray-500">Job ID: {job.job_id}</p>
            </div>
          </div>

          {/* Draft exercises */}
          {job.draft_exercises && job.draft_exercises.length > 0 && (
            <div className="space-y-3 mt-4">
              {job.draft_exercises.map((ex, idx) => (
                <div key={ex.exercise_id || idx} className="rounded-lg border border-gray-100 p-4">
                  <div className="flex items-start gap-3">
                    <FileText className="h-4 w-4 text-gray-400 mt-0.5 shrink-0" />
                    <div>
                      <h4 className="text-sm font-medium text-gray-900">{ex.title}</h4>
                      <p className="text-xs text-gray-500 mt-0.5">{ex.description || ex.mission_markdown?.slice(0, 100)}</p>
                      <div className="mt-2 flex gap-2">
                        <span className="text-[10px] text-gray-400 uppercase">{ex.language}</span>
                        <span className="text-[10px] text-gray-400">·</span>
                        <span className="text-[10px] text-gray-400">{ex.difficulty}</span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}

              {job.status === 'awaiting_approval' && (
                <button
                  onClick={handlePublish}
                  className="inline-flex items-center gap-2 rounded-lg bg-gray-900 px-4 py-2.5 text-sm font-medium text-white hover:bg-gray-800 transition-colors"
                >
                  <CheckCircle2 className="h-4 w-4" />
                  Aprobar y Publicar
                </button>
              )}
            </div>
          )}

          {polling && (
            <p className="text-xs text-gray-400 mt-3 flex items-center gap-2">
              <Spinner size="sm" /> Verificando estado...
            </p>
          )}

          {job.status === 'completed' && job.activity_id && (
            <p className="text-sm text-emerald-600 mt-3">
              {job.exercise_count} ejercicios publicados exitosamente
            </p>
          )}
        </div>
      )}
    </div>
  )
}
