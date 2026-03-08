import {expect, Locator, Page} from "@playwright/test";

export abstract class PageObject {

    protected constructor(
        public page: Page,
    ) {}

    abstract url(): string;

    abstract expectToBeShown(): Promise<this>;

}
