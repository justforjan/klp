import {test} from '../fixtures';

test.describe('Events Page', () => {

    test.describe('search', () => {

        test('by date', async ({ eventsPage }) => {

            await eventsPage.search({startDate: '2024-07-01', endDate: '2024-07-02'});
            await eventsPage.expectNrOfSearchResultsToBe(4);

        })

    })


})
