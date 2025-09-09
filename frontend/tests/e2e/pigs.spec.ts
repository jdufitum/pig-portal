import { test, expect } from '@playwright/test'

const owner = { email: 'owner@farm.test', password: 'Passw0rd!' }

async function login(page){
  await page.goto('/login')
  await page.getByLabel('Email').fill(owner.email)
  await page.getByLabel('Password').fill(owner.password)
  await page.getByRole('button', { name: 'Sign in' }).click()
  await expect(page).toHaveURL(/\/$/)
}

test('pigs list and create', async ({ page }) => {
  await login(page)
  await page.getByRole('link', { name: 'Pigs' }).click()
  await expect(page.getByText('Pigs')).toBeVisible()
  await page.getByRole('button', { name: 'Create' }).click()
  await page.getByLabel('Ear tag').fill('TEST-100')
  await page.getByRole('button', { name: 'Create' }).click()
  await expect(page.getByRole('link', { name: 'TEST-100' })).toBeVisible()
  await page.getByLabel('Search').fill('TEST-100')
  await page.getByRole('button', { name: 'Filter' }).click()
  await expect(page.getByRole('link', { name: 'TEST-100' })).toBeVisible()
})

test('pig detail tabs and actions', async ({ page }) => {
  await login(page)
  await page.getByRole('link', { name: 'Pigs' }).click()
  await page.getByRole('link', { name: 'TEST-100' }).click()
  await expect(page.getByText('Pig Detail')).toBeVisible()
  // Add weight
  await page.getByRole('button', { name: 'weights' }).click()
  const today = new Date().toISOString().slice(0,10)
  await page.locator('input[type="date"]').fill(today)
  await page.locator('input[type="number"]').fill('55')
  await page.getByRole('button', { name: 'Add' }).click()
  await expect(page.getByText(today)).toBeVisible()
  // Health: just ensure tab loads
  await page.getByRole('button', { name: 'health' }).click()
  // Files upload
  await page.getByRole('button', { name: 'files' }).click()
  const filePath = 'frontend/public/vite.svg'
  await page.locator('input[type="file"]').setInputFiles(filePath)
  await expect(page.locator('img').first()).toBeVisible()
})

