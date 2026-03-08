import {expect, Locator, Page} from "@playwright/test";
import {KlpPage} from "./KlpPage";

export class HomePage extends KlpPage{

    constructor(
        public page: Page,
        private title = page.getByRole("heading", {name: "Willkommen zur Kulturellen Landpartie"}),
    ) { super(page)}

    url(): string {
        return "/";
    }

    async expectToBeShown(): Promise<this> {
        await expect(this.title).toBeVisible()
        await expect(this.page.getByRole("link", {name: "Termine durchsuchen"})).toBeVisible();
        await expect(this.page.getByRole("link", {name: "Karte ansehen"})).toBeVisible();
        return super.expectToBeShown();
    };
}
