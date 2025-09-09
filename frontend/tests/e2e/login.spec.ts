import { test, expect } from '@playwright/test'

const owner = { email: 'owner@farm.test', password: 'Passw0rd!' }

async function waitBackendReady(page){
  for (let i=0;i<60;i++){
    const resp = await page.request.get('http://localhost/api/healthz')
    if (resp.ok()) return
    await page.waitForTimeout(1000)
  }
  throw new Error('backend not ready')
}

test.beforeAll(async ({ request }) => {
  await waitBackendReady({ request, waitForTimeout: (ms:number)=>new Promise(r=>setTimeout(r,ms)) } as any)
})

test('login success and error flow', async ({ page }) => {
  await page.goto('/login')
  await page.getByLabel('Email').fill(owner.email)
  await page.getByLabel('Password').fill('wrong')
  await page.getByRole('button', { name: 'Sign in' }).click()
  await expect(page.getByText('Login failed')).toBeVisible()

  await page.getByLabel('Password').fill(owner.password)
  await page.getByRole('button', { name: 'Sign in' }).click()
  await expect(page).toHaveURL(/\/$/)
})

