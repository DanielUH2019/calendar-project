import { expect, test } from "@playwright/test"
import { createUser } from "./utils/privateApi"
import { randomEmail, randomPassword, randomRoomName } from "./utils/random"
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
    await expect(
      page.getByRole("heading", { name: "Your reservations" }),
    ).toBeVisible()
    await expect(page.getByTestId("my-reservations-empty")).toBeVisible()
    await expect(page.getByLabel("Start date")).toBeVisible()
    await expect(page.getByLabel("End date")).toBeVisible()
    await expect(page.getByLabel("Number of people")).toBeVisible()
    await expect(
      page.getByRole("button", { name: "Search", exact: true }),
    ).toBeVisible()
  })

  test("search shows empty state when user has no rooms", async ({ page }) => {
    await page.goto("/reservations")

    await page.getByLabel("Start date").fill("2026-06-01")
    await page.getByLabel("End date").fill("2026-06-05")
    await page.getByLabel("Number of people").fill("2")
    await page.getByRole("button", { name: "Search", exact: true }).click()

    await expect(page.getByTestId("available-rooms-results")).toBeVisible()
    await expect(page.getByTestId("available-rooms-empty")).toBeVisible()
    await expect(page.getByText("No rooms match your search.")).toBeVisible()
  })

  test("search lists room after creating a room", async ({ page }) => {
    const name = randomRoomName()

    await page.goto("/rooms")
    await page.getByRole("button", { name: "Add Room" }).click()
    await page.getByLabel("Name").fill(name)
    await page.getByLabel(/Max number of people/i).fill("4")
    await page.getByRole("button", { name: "Save" }).click()
    await expect(page.getByText("Room created successfully")).toBeVisible()

    await page.goto("/reservations")
    await page.getByLabel("Start date").fill("2026-07-01")
    await page.getByLabel("End date").fill("2026-07-10")
    await page.getByLabel("Number of people").fill("2")
    await page.getByRole("button", { name: "Search", exact: true }).click()

    await expect(page.getByTestId("available-rooms-results")).toBeVisible()
    const item = page
      .getByTestId("available-room-item")
      .filter({ hasText: name })
    await expect(item).toBeVisible()
    await expect(item).toContainText("Up to 4 people")
  })

  test("your reservations lists booking after reserve", async ({ page }) => {
    const name = randomRoomName()

    await page.goto("/rooms")
    await page.getByRole("button", { name: "Add Room" }).click()
    await page.getByLabel("Name").fill(name)
    await page.getByLabel(/Max number of people/i).fill("4")
    await page.getByRole("button", { name: "Save" }).click()
    await expect(page.getByText("Room created successfully")).toBeVisible()

    await page.goto("/reservations")
    await expect(page.getByTestId("my-reservations-empty")).toBeVisible()

    await page.getByLabel("Start date").fill("2026-10-01")
    await page.getByLabel("End date").fill("2026-10-08")
    await page.getByLabel("Number of people").fill("2")
    await page.getByRole("button", { name: "Search", exact: true }).click()

    await page
      .getByTestId("available-room-item")
      .filter({ hasText: name })
      .getByRole("button", { name: "Reserve" })
      .click()

    await expect(page.getByText("Reservation created")).toBeVisible()
    await expect(
      page.getByTestId("my-reservations-item").filter({ hasText: name }),
    ).toBeVisible()
  })
})
