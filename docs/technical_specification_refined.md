# Technical Specification - Refined

## Application Overview

The KLP (Kulturelle Landpartie) website provides information about an annual cultural event in the Wendland region of Germany. The website enables visitors to:
- Browse and filter events by date and description
- View location details with event schedules
- Explore locations on an interactive map
- Mark events as favorites for easy access

The application should be modern, responsive, and work seamlessly on both desktop and mobile devices.

## Technologies & Tools

### Environment
- **Package Manager:** uv
- **Python Version:** 3.12

### Backend
- **Framework:** FastAPI
- **ORM:** SQLModel
- **Database:** PostgreSQL
- **Migrations:** Alembic (recommended for schema management)

### Frontend
- **Templating:** FastAPI Jinja2 Templates (server-rendered pages)
- **Styling:** Tailwind CSS
- **JavaScript:** Vanilla JS + HTMX for progressive enhancement
  - HTMX for dynamic filtering and updates
  - Map interactivity (Leaflet.js for OpenStreetMap)
  - Favorites management (client-side localStorage)

### Deployment
- **Containerization:** Docker
- **Orchestration:** Docker Compose

### External Libraries
- **Map Library:** Leaflet.js (for OpenStreetMap integration)
- **Web Scraping:** BeautifulSoup4 or httpx + parsel
- **Task Scheduling:** APScheduler or similar for scraping jobs
- **HTMX:** For dynamic page updates without full page reloads

## Data Model

### Entities & Relationships

#### Event
Represents a specific event happening at the KLP.

**Fields:**
- `id`: int (primary key)
- `name`: str (required)
- `description`: str (optional, can be long text)
- `location_id`: int (foreign key to Location)
- `payment_type`: str (enum: "free", "hat_collection", "fixed_price", "hat_plus_materials")
- `entry_price`: decimal (optional, for fixed price events)
- `material_cost`: decimal (optional, additional material fees)
- `booking_required`: bool (default: False)
- `organizer`: str (optional, person/group organizing)

**Relationships:**
- Many-to-One with Location
- One-to-Many with EventOccurrence

#### EventOccurrence
Represents a specific date/time when an event happens.

**Fields:**
- `id`: int (primary key)
- `event_id`: int (foreign key to Event)
- `start_datetime`: datetime (required)
- `end_datetime`: datetime (optional)
- `is_cancelled`: bool (default: False, allows individual occurrence cancellations)

**Relationships:**
- Many-to-One with Event

**Rationale:** Events can happen multiple times (e.g., "30.05. 11:00, 31.05. 11:00, 07.06. 11:00"), so we need a separate table to track each occurrence while keeping event details (name, description) in one place.

#### Location
Represents a venue where events take place.

**Fields:**
- `id`: int (primary key)
- `name`: str (required)
- `subtitle`: str (optional, e.g., "IM VERMEINTLICH WILDEN GARTEN")
- `address`: str (required)
- `phone`: str (optional)
- `email`: str (optional)
- `latitude`: decimal (required for map)
- `longitude`: decimal (required for map)
- `google_maps_link`: str (optional)
- `links`: list[str] (PostgreSQL array, optional, for additional URLs like website, social media)

**Relationships:**
- One-to-Many with Event
- Many-to-Many with BikeTour

#### BikeTour
Represents a cycling route that passes through various locations.

**Fields:**
- `id`: int (primary key)
- `number`: int (unique, e.g., 4 for "Fahrradtour: 4")
- `komoot_link`: str (optional, URL to route on Komoot)
- `created_at`: datetime
- `updated_at`: datetime

**Relationships:**
- Many-to-Many with Location (via LocationBikeTour junction table)

#### LocationBikeTour
Junction table for the many-to-many relationship between Location and BikeTour.

**Fields:**
- `id`: int (primary key)
- `location_id`: int (foreign key to Location)
- `bike_tour_id`: int (foreign key to BikeTour)
- `order`: int (optional, for route ordering)

**Rationale:** Multiple bike tours can pass through the same location, and one bike tour passes through multiple locations.

### Entity Relationship Diagram (ERD)

```
Location (1) ---- (*) Event (1) ---- (*) EventOccurrence

Location (*) ---- (*) BikeTour
         (via LocationBikeTour)
```

## Data Source & Web Scraping

### Source URLs
- **Events:** `https://www.kulturelle-landpartie.de/termine/{DD-MM}.html` (e.g., 29-05.html)
- **Locations:** `https://www.kulturelle-landpartie.de/orte/{location-slug}.html` (e.g., bankewitz.html)

### Scraping Strategy

#### Event Scraping
Parse the HTML structure:
```html
<div class="row">
    <div><b>29.05.</b> — <nobr>09:00</nobr> | <a href="/radrouten.html#t4">Fahrradtour:<span class="num">4</span></a></div>
    <div><b>Event Name</b><br>Description...<br>Eintritt: Hutkasse</div>
    <div><a href="/orte/location-slug.html">LOCATION NAME</a> (Organizer)</div>
</div>
```

**Extraction Logic:**
- Date + time from first div
- Event name (bold text in second div)
- Description (text after event name)
- Payment info (extract from text like "Eintritt: Hutkasse", "Hutkasse & 20 € Mat.", "Eintritt frei")
- Location slug from href in third div
- Organizer from text in parentheses
- Bike tour number from link in first div

**Challenges:**
- Payment type variations (free, hat, hat+materials, fixed price)
- Multi-date events need parsing
- Cancellations marked as "Fällt leider aus" in event name/description

#### Location Scraping
Parse the HTML structure for location details and associated events.

**Extraction Logic:**
- Name from `<h1 class="norm">` tag
- Subtitle from `<h3>` tag
- Address, phone, email from contact block
- Email is obfuscated with JavaScript - decode using the encoded string
- Website from links
- Bike tour numbers from `<a href="/radrouten.html#t{number}">`
- Events listed on location page (cross-reference with event scraping)

**Email Decoding:**
```python
# Decode JavaScript obfuscated emails
# Example: eval(decodeURIComponent('%64%6f%63%75...'))
import urllib.parse
decoded = urllib.parse.unquote(encoded_string)
# Then parse the resulting mailto: link
```

#### Scraping Schedule
- **Frequency:** Twice daily (e.g., 6:00 AM and 6:00 PM)
- **Strategy:** Full reload of dataset each time
- **Error Handling:**
  - Log scraping failures
  - Retain previous data if scrape fails
  - Alert if data hasn't updated in 48 hours
  - Validate scraped data before replacing existing data

#### Data Validation
Before persisting scraped data:
- Required fields must be present (name, location for events)
- Dates must be valid
- URLs must be properly formatted
- Detect duplicate entries

#### Scraping Implementation
- Use session pooling for HTTP requests
- Implement rate limiting to be respectful to source server
- Cache parsed location data to avoid redundant scraping
- Store raw HTML for debugging purposes (optional)

## Favorites Feature

### Storage Strategy
**Client-side only** using `localStorage`:
- No user authentication required
- Simple implementation
- Works offline
- Data persists across sessions

### Implementation
- Store array of event IDs in localStorage
- Vanilla JavaScript toggles favorites on/off
- Server endpoint accepts comma-separated event IDs to filter and render favorites page
- Favorite button uses HTMX to update UI state

## User Interface & Pages

### Pages

1. **Events Page** (`/events`)
   - List view with filtering
   - Filters: date range, text search
   - Default sort: date ascending
   - Responsive grid layout

2. **Locations Page** (`/locations`)
   - Alphabetically sorted list
   - Calendar-like display of events per location
   - Responsive grid layout

3. **Location Detail Page** (`/locations/{id}`)
   - Full location information
   - Event schedule
   - Map with marker
   - Associated bike tours

4. **Map Page** (`/map`)
   - OpenStreetMap with Leaflet.js
   - Markers for each location
   - Clickable popups with location name
   - Links to location detail pages

5. **Favorites Page** (`/favorites`)
   - Calendar-like display of favorited events
   - Similar UI to locations event display

### Navigation
- Main menu: Events, Locations, Map, Favorites
- Mobile: Hamburger menu
- Desktop: Horizontal navigation bar

### Responsive Design
- Mobile-first approach with Tailwind CSS
- Breakpoints: sm (640px), md (768px), lg (1024px)
- Touch-friendly buttons and interactive elements

## Development Workflow

### Incremental Implementation
Implement user stories in order:
1. Implement core data models and database schema
2. Build scraping functionality and data ingestion
3. User Story 1: List Events with Filtering
4. User Story 2: Show Locations
5. User Story 3: Map Integration
6. User Story 4: Favorites Feature

### After Each User Story
1. Test functionality thoroughly
2. Ensure responsive design works
3. Commit changes with clear message
4. Brief explanation of implementation
5. Move to next user story only when current is complete

### Code Quality
- Type hints for all Python functions
- Minimal comments (explain "why", not "what")
- Follow FastAPI best practices
- Reusable Jinja2 components
- Tailwind utility classes (avoid custom CSS)

### Testing Strategy
- Manual testing for each user story
- Test on multiple devices/screen sizes
- Validate against acceptance criteria
- Future: Add automated tests (pytest, Playwright)

## Design Decisions

### Data Model
- **Event Occurrences:** Using EventOccurrence model to track multiple dates for the same event
- **Cancellations:** Cancelled events will be displayed with visual indicator (strikethrough, badge, etc.)
- **Data Cleanup:** Data deleted from source will naturally be removed on next scrape (no soft delete needed)

### Frontend Architecture
- **Server-Rendered Pages:** All pages rendered with Jinja2 templates
- **HTMX:** Used for dynamic filtering and UI updates without full page reloads
- **Favorites:** Client-side localStorage only (no authentication needed)

### External Features
- **Bike Tours:** Display bike tour numbers and link directly to Komoot (no route visualization)

### Performance (Current Scope)
- **No caching layer** initially - keep it simple
- **No database indexes** yet - optimize when/if needed
- **No CDN** - serve static assets directly from application server

## Security Considerations
- Validate and sanitize all scraped content before display
- Use parameterized queries (SQLModel handles this)
- CORS configuration if API endpoints are exposed
- Rate limiting on public endpoints
- No sensitive data storage (no user accounts initially)

## Performance Considerations (Future)
- Add database indexes on frequently queried fields if performance issues arise
- Implement pagination for event listings if dataset grows large
- Consider lazy loading for map markers if many locations
- Minify CSS/JS for production builds
- Server-side caching when needed

## Deployment Configuration

### Docker Setup
```yaml
services:
  web:
    - FastAPI application
    - Uvicorn server
  db:
    - PostgreSQL 15+
  scraper:
    - Scheduled scraping service
```

### Environment Variables
- `DATABASE_URL`: PostgreSQL connection string
- `SCRAPE_SCHEDULE`: Cron expression for scraping
- `SECRET_KEY`: For session management (if needed)
- `DEBUG`: Boolean for development mode
