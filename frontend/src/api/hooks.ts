import { useQuery, useMutation } from '@tanstack/react-query'
import { api, useAuthStore } from './client'

export function useLogin() {
  const setTokens = useAuthStore.getState().setTokens
  return useMutation({
    mutationFn: async (payload: { email: string, password: string }) => {
      const form = new URLSearchParams()
      form.set('username', payload.email)
      form.set('password', payload.password)
      const { data } = await api.post('/auth/login', form)
      return data
    },
    onSuccess: (data) => {
      setTokens(data.access_token, data.refresh_token)
    }
  })
}

export function usePigs(params?: { search?: string }) {
  return useQuery({
    queryKey: ['pigs', params?.search],
    queryFn: async () => {
      const { data } = await api.get('/pigs', { params })
      return data as any[]
    }
  })
}
