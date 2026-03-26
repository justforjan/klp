import {expect, Locator, Page} from "@playwright/test";
import {KlpPage} from "./KlpPage";

export class Events extends KlpPage {

    constructor(
        public page: Page,
        protected form = page.locator("#filter-form"),
        protected eventsList = page.locator("div#event-list"),
        protected events = page.locator("div#event-list > div")
    ) {
        super(page)
    }

    url(): string {
        return "/events";
    }

    async expectToBeShown(): Promise<this> {
        await expect(this.form).toBeVisible();
        await expect(this.eventsList).toBeVisible();
        await this.expectNrOfSearchResultsToBe(4)
        return super.expectToBeShown();
    };

    async expectNrOfSearchResultsToBe(nr: number): Promise<this> {
        await expect(this.events).toHaveCount(nr);
        return this;
    }

    async search({
        startDate = '2024-07-01',
        endDate = '2024-07-02',
        text = '',
        location = '',
        showCancelled = '',
        entryType = ''
    }: {
        startDate?: string,
        endDate?: string,
        text?: string,
        location?: string,
        showCancelled?: string,
        entryType?: string
    } = {}): Promise<this> {
        await this.form.getByLabel("Von Datum").fill(startDate);
        await this.form.getByLabel("Bis Datum").fill(endDate);
        await this.form.getByLabel("Suche").fill(text);
        await this.form.getByLabel("Ort").fill(location);
        await this.form.getByLabel("Abgesagte Termin").fill(showCancelled)
        await this.form.getByLabel("Eintrittsart").fill(entryType);
        await this.form.getByRole("button", {name: "Filtern"}).click();
        return this
    }

    async goToLocationDetails(locationName: string): Promise<void> {}
}
