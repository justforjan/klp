import { test as base } from '@playwright/test';
import {HomePage} from "./pages/HomePage";
import {Events} from "./pages/Events";

type Fixtures = {
    homePage: HomePage,
    eventsPage: Events,
}

export const test = base.extend<Fixtures>({
    homePage: async ({ page }, use) => {
        const homePage = new HomePage(page);
        await page.goto(homePage.url());
        await homePage.expectToBeShown();
        await use(homePage);
    },
    eventsPage: async ({ page }, use) => {
        const events = new Events(page);
        await page.goto(events.url());
        await events.expectToBeShown();
        await use(events);
    }
});

export { expect } from '@playwright/test';