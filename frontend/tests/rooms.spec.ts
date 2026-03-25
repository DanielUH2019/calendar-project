import { expect, test } from "@playwright/test"
import { createUser } from "./utils/privateApi"
import { randomEmail, randomPassword, randomRoomName } from "./utils/random"
import { logInUser } from "./utils/user"

test("Rooms page is accessible and shows correct title", async ({ page }) => {
  await page.goto("/rooms")
  await expect(page.getByRole("heading", { name: "Rooms" })).toBeVisible()
  await expect(page.getByText("Create and manage your rooms")).toBeVisible()
})

test("Add Room button is visible", async ({ page }) => {
  await page.goto("/rooms")
  await expect(page.getByRole("button", { name: "Add Room" })).toBeVisible()
})

test.describe("Rooms management", () => {
  test.use({ storageState: { cookies: [], origins: [] } })
  let email: string
  const password = randomPassword()

  test.beforeAll(async () => {
    email = randomEmail()
    await createUser({ email, password })
  })

  test.beforeEach(async ({ page }) => {
    await logInUser(page, email, password)
    await page.goto("/rooms")
  })

  test("Create a new room successfully", async ({ page }) => {
    const name = randomRoomName()

    await page.getByRole("button", { name: "Add Room" }).click()
    await page.getByLabel("Name").fill(name)
    await page.getByLabel(/Max number of people/i).fill("4")
    await page.getByRole("button", { name: "Save" }).click()

    await expect(page.getByText("Room created successfully")).toBeVisible()
    await expect(page.getByText(name)).toBeVisible()
  })

  test("Create room with only required fields", async ({ page }) => {
    const name = randomRoomName()

    await page.getByRole("button", { name: "Add Room" }).click()
    await page.getByLabel("Name").fill(name)
    await page.getByRole("button", { name: "Save" }).click()

    await expect(page.getByText("Room created successfully")).toBeVisible()
    await expect(page.getByText(name)).toBeVisible()
  })

  test("Cancel room creation", async ({ page }) => {
    await page.getByRole("button", { name: "Add Room" }).click()
    await page.getByLabel("Name").fill("Test Room")
    await page.getByRole("button", { name: "Cancel" }).click()

    await expect(page.getByRole("dialog")).not.toBeVisible()
  })

  test("Name is required", async ({ page }) => {
    await page.getByRole("button", { name: "Add Room" }).click()
    await page.getByLabel("Name").fill("")
    await page.getByLabel("Name").blur()

    await expect(page.getByText("Name is required")).toBeVisible()
  })

  test.describe("Edit and Delete", () => {
    let roomName: string

    test.beforeEach(async ({ page }) => {
      roomName = randomRoomName()

      await page.getByRole("button", { name: "Add Room" }).click()
      await page.getByLabel("Name").fill(roomName)
      await page.getByRole("button", { name: "Save" }).click()
      await expect(page.getByText("Room created successfully")).toBeVisible()
      await expect(page.getByRole("dialog")).not.toBeVisible()
    })

    test("Edit a room successfully", async ({ page }) => {
      const roomRow = page.getByRole("row").filter({ hasText: roomName })
      await roomRow.getByRole("button").last().click()
      await page.getByRole("menuitem", { name: "Edit Room" }).click()

      const updatedName = randomRoomName()
      await page.getByLabel("Name").fill(updatedName)
      await page.getByRole("button", { name: "Save" }).click()

      await expect(page.getByText("Room updated successfully")).toBeVisible()
      await expect(page.getByText(updatedName)).toBeVisible()
    })

    test("Delete a room successfully", async ({ page }) => {
      const roomRow = page.getByRole("row").filter({ hasText: roomName })
      await roomRow.getByRole("button").last().click()
      await page.getByRole("menuitem", { name: "Delete Room" }).click()

      await page.getByRole("button", { name: "Delete" }).click()

      await expect(
        page.getByText("The room was deleted successfully"),
      ).toBeVisible()
      await expect(page.getByText(roomName)).not.toBeVisible()
    })
  })
})

test.describe("Rooms empty state", () => {
  test.use({ storageState: { cookies: [], origins: [] } })

  test("Shows empty state message when no rooms exist", async ({ page }) => {
    const email = randomEmail()
    const password = randomPassword()
    await createUser({ email, password })
    await logInUser(page, email, password)

    await page.goto("/rooms")

    await expect(page.getByText("You don't have any rooms yet")).toBeVisible()
    await expect(page.getByText("Add a new room to get started")).toBeVisible()
  })
})
