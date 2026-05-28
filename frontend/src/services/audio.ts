import axios from 'axios'

const API_BASE_URL = 'http://127.0.0.1:5001'

const api = axios.create({ baseURL: API_BASE_URL })

export interface VoiceOption {
  voice_id: string
  name: string
}

export interface DialogueInput {
  text: string
  voice_id: string
}

export async function listElevenLabsVoices(): Promise<{
  voices: VoiceOption[]
  warning?: string
  hint?: string
}> {
  const { data } = await api.get<{
    voices: VoiceOption[]
    warning?: string
    hint?: string
  }>('/audio/voices')
  return { voices: data.voices ?? [], warning: data.warning, hint: data.hint }
}

export async function convertDialogueToAudio(
  inputs: DialogueInput[],
  modelId?: string
): Promise<{ audio_file: string; url: string }> {
  const { data } = await api.post<{
    audio_file: string
    url: string
  }>('/dialogue/convert', {
    inputs,
    ...(modelId ? { model_id: modelId } : {}),
  })
  return { audio_file: data.audio_file, url: data.url }
}

export async function generateAudioFromScript(payload: {
  script: string
  voice_map: Record<string, string>
  default_voice_id: string
  model_id?: string
  enhance_emotion?: boolean
}): Promise<{ audio_file: string; url: string }> {
  const { data } = await api.post<{
    audio_file: string
    url: string
  }>('/audio/generate-from-script', payload)
  return { audio_file: data.audio_file, url: data.url }
}

export async function enhanceDialogueText(text: string): Promise<string> {
  const { data } = await api.post<{ enhanced_text: string }>('/dialogue/enhance', { text })
  return data.enhanced_text
}
