import type { FullConfig } from '@playwright/test'

export default async function globalSetup(config: FullConfig) {
  const request = await config.projects[0].use?.request?.newContext?.() || (await import('@playwright/test')).request.newContext()
  for (let i = 0; i < 60; i++) {
    try {
      const resp = await request.get('http://localhost/api/healthz')
      if (resp.ok()) return
    } catch {}
    await new Promise(r => setTimeout(r, 1000))
  }
  // Seed test users if backend ready
  const users = [
    { email: 'worker@farm.test', name: 'Worker', password: 'Passw0rd!', role: 'worker' },
    { email: 'vet@farm.test', name: 'Vet', password: 'Passw0rd!', role: 'vet' },
  ]
  for (const u of users) {
    try {
      await request.post('http://localhost/api/v1/auth/register', { data: u })
    } catch {}
  }
}

