import {expect, Locator, Page} from "@playwright/test";
import {PageObject} from "./PageObject";

export abstract class KlpPage extends PageObject{

    protected constructor(
        public page: Page,
        protected home = page.getByRole("link", {name: "Kulturelle Landpartie", exact: true}),
        protected events = page.getByRole("link", {name: "Termine", exact: true}),
        protected locations = page.getByRole("link", {name: "Orte", exact: true}),
        protected map = page.getByRole("link", {name: "Karte", exact: true}),
        protected favourites = page.getByRole("link", {name: "Favoriten", exact: true}),
    ) {
        super(page);
    }

    abstract url(): string;

    async expectToBeShown(): Promise<this> {
        await expect(this.page).toHaveURL(this.url());
        await this.navBarIsShown();
        return this;
    };

    async navBarIsShown() {
        await expect(this.home).toBeVisible();
        await expect(this.events).toBeVisible();
        await expect(this.locations).toBeVisible();
        await expect(this.map).toBeVisible();
        await expect(this.favourites).toBeVisible();
    }

    async goToHome() {
        await this.home.click();
    }

    async goToEvents() {
        await this.events.click();
    }

    async goToMap() {
        await this.map.click();
    }

    async goToFavourites() {
        await this.favourites.click();
    }
}
