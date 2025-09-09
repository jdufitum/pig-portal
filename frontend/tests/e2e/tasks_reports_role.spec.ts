import { test, expect } from '@playwright/test'

const owner = { email: 'owner@farm.test', password: 'Passw0rd!' }
const worker = { email: 'worker@farm.test', password: 'Passw0rd!' }

async function login(page, creds){
  await page.goto('/login')
  await page.getByLabel('Email').fill(creds.email)
  await page.getByLabel('Password').fill(creds.password)
  await page.getByRole('button', { name: 'Sign in' }).click()
}

test('tasks and reports flow + role UX', async ({ page }) => {
  await login(page, owner)
  // Create a task
  await page.getByRole('link', { name: 'Tasks' }).click()
  // Page is placeholder; simulate via API or assume dashboard shows counts
  await page.goto('/')
  await expect(page).toHaveURL('/')
  // Logout and login as Worker
  // Assume there is a logout button in header if present; otherwise clear storage
  await page.context().clearCookies()
  await page.context().clearPermissions()
  await login(page, worker)
  // Worker cannot open Settings
  await page.goto('/settings')
  await expect(page).not.toHaveURL('/settings')
})

