import { useState, useRef, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'
import studentService, { type ChatResponse } from '../../services/student.service'
import { toast } from '../../hooks/useToast'
import Spinner from '../../components/ui/Spinner'
import { ArrowLeft, Send, Bot, User, BookOpen } from 'lucide-react'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  ragUsed?: boolean
}

export default function StudentTutor() {
  const { activityId } = useParams<{ activityId: string }>()
  const { user } = useAuth()
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const [currentCode, setCurrentCode] = useState('')
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSend = async () => {
    if (!user || !activityId || !input.trim() || sending) return
    const userMsg: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim(),
      timestamp: new Date(),
    }
    setMessages((prev) => [...prev, userMsg])
    const question = input.trim()
    setInput('')
    setSending(true)
    try {
      const res: ChatResponse = await studentService.chatWithTutor(activityId, user.id, {
        message: question,
        current_code: currentCode || undefined,
      })
      const assistantMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: res.response,
        timestamp: new Date(),
        ragUsed: res.rag_context_used,
      }
      setMessages((prev) => [...prev, assistantMsg])
    } catch {
      toast({ title: 'Error de comunicación con el tutor', variant: 'error' })
    } finally {
      setSending(false)
    }
  }

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)]">
      {/* Header */}
      <div className="flex items-center gap-4 pb-4">
        <Link to={`/activities/${activityId}`} className="rounded-lg p-2 hover:bg-gray-100 transition-colors">
          <ArrowLeft className="h-5 w-5 text-gray-500" />
        </Link>
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-full bg-gray-900">
            <Bot className="h-5 w-5 text-white" />
          </div>
          <div>
            <h1 className="text-sm font-semibold text-gray-900">Tutor IA Socrático</h1>
            <p className="text-xs text-gray-500">Te guío paso a paso sin darte la respuesta directamente</p>
          </div>
        </div>
      </div>

      {/* Code context toggle */}
      <div className="mb-3">
        <details className="rounded-lg border border-gray-100 bg-white">
          <summary className="flex items-center gap-2 px-4 py-2.5 text-xs font-medium text-gray-600 cursor-pointer hover:bg-gray-50">
            <BookOpen className="h-3.5 w-3.5" />
            Compartir código actual con el tutor (opcional)
          </summary>
          <textarea
            value={currentCode}
            onChange={(e) => setCurrentCode(e.target.value)}
            className="w-full border-t border-gray-100 p-3 font-mono text-xs text-gray-800 bg-gray-50 resize-none h-32 focus:outline-none"
            placeholder="Pegá tu código aquí para que el tutor pueda ayudarte mejor..."
          />
        </details>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto rounded-xl border border-gray-100 bg-white">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center p-8">
            <div className="flex h-14 w-14 items-center justify-center rounded-full bg-gray-100 mb-4">
              <Bot className="h-7 w-7 text-gray-400" />
            </div>
            <p className="text-sm font-medium text-gray-900">¡Hola! Soy tu tutor IA</p>
            <p className="mt-1 text-xs text-gray-500 max-w-sm">
              Puedo ayudarte con esta actividad usando preguntas que te guíen a encontrar la solución por tu cuenta. 
              ¿En qué puedo ayudarte?
            </p>
          </div>
        ) : (
          <div className="p-4 space-y-4">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                {msg.role === 'assistant' && (
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gray-900 shrink-0 mt-0.5">
                    <Bot className="h-4 w-4 text-white" />
                  </div>
                )}
                <div
                  className={`max-w-[75%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                    msg.role === 'user'
                      ? 'bg-gray-900 text-white'
                      : 'bg-gray-100 text-gray-800'
                  }`}
                >
                  <p className="whitespace-pre-wrap">{msg.content}</p>
                  {msg.ragUsed && (
                    <p className="mt-2 text-[10px] opacity-60 flex items-center gap-1">
                      <BookOpen className="h-3 w-3" /> Respuesta basada en material del curso
                    </p>
                  )}
                </div>
                {msg.role === 'user' && (
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gray-200 shrink-0 mt-0.5">
                    <User className="h-4 w-4 text-gray-600" />
                  </div>
                )}
              </div>
            ))}
            {sending && (
              <div className="flex gap-3">
                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gray-900 shrink-0">
                  <Bot className="h-4 w-4 text-white" />
                </div>
                <div className="bg-gray-100 rounded-2xl px-4 py-3">
                  <div className="flex gap-1">
                    <div className="h-2 w-2 rounded-full bg-gray-400 animate-bounce" style={{ animationDelay: '0ms' }} />
                    <div className="h-2 w-2 rounded-full bg-gray-400 animate-bounce" style={{ animationDelay: '150ms' }} />
                    <div className="h-2 w-2 rounded-full bg-gray-400 animate-bounce" style={{ animationDelay: '300ms' }} />
                  </div>
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>
        )}
      </div>

      {/* Input */}
      <div className="mt-3 flex gap-3">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && handleSend()}
          placeholder="Escribí tu pregunta..."
          className="flex h-11 flex-1 rounded-lg border border-gray-200 bg-white px-4 text-sm placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent transition-shadow"
        />
        <button
          onClick={handleSend}
          disabled={sending || !input.trim()}
          className="inline-flex h-11 w-11 items-center justify-center rounded-lg bg-gray-900 text-white hover:bg-gray-800 disabled:opacity-50 transition-colors shrink-0"
        >
          <Send className="h-4 w-4" />
        </button>
      </div>
    </div>
  )
}
