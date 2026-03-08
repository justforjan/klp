import {expect, Locator, Page} from "@playwright/test";
import {KlpPage} from "./KlpPage";

export class Events extends KlpPage{

    constructor(
        public page: Page,
    ) { super(page) }

    url(): string {
        return "/events";
    }

    async expectToBeShown(): Promise<this> {
        return super.expectToBeShown();
    };
}
