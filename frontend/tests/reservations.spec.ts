import { expect, test } from "@playwright/test"
import { createUser } from "./utils/privateApi"
import { randomEmail, randomPassword } from "./utils/random"
import { logInUser } from "./utils/user"

test.describe("Reservations page", () => {
  test.use({ storageState: { cookies: [], origins: [] } })

  test.beforeEach(async ({ page }) => {
    const email = randomEmail()
    const password = randomPassword()
    await createUser({ email, password })
    await logInUser(page, email, password)
  })

  test("shows search form fields", async ({ page }) => {
    await page.goto("/reservations")

    await expect(
      page.getByRole("heading", { name: "Reservations" }),
    ).toBeVisible()
    await expect(page.getByLabel("Start date")).toBeVisible()
    await expect(page.getByLabel("End date")).toBeVisible()
    await expect(page.getByLabel("Number of people")).toBeVisible()
    await expect(
      page.getByRole("button", { name: "Search", exact: true }),
    ).toBeVisible()
  })

  test("shows placeholder toast on search submit", async ({ page }) => {
    await page.goto("/reservations")

    await page.getByLabel("Start date").fill("2026-06-01")
    await page.getByLabel("End date").fill("2026-06-05")
    await page.getByLabel("Number of people").fill("2")
    await page.getByRole("button", { name: "Search", exact: true }).click()

    await expect(page.getByText("Search is not connected yet")).toBeVisible()
  })
})
