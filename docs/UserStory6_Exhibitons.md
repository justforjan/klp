As a website visitor I want to see what exhibitions are exhibited at a location.

Acceptance Criteria:
1. There should be a section on the location page that lists the exhibitions at that location.
2. Each exhibition listed should include the exhibition name, description.

Technical Notes:
Also create a new table in the database to store exhibition information, with the following attributes:
- name
- description (optional)
- location_id (foreign key referencing the location table)
- artist
- link to arist page on the original website (optional)
- image path (optional)

You can find the exhibition information by scraping the original location page. 

Look for this div:
```html
<div class="slider aus slick-initialized slick-slider
```

Within this div, you can find a list of divs of this structure:
```html
<div class="item slick-slide slick-active" style="width: 145px;" data-slick-index="7" aria-hidden="false" tabindex="0" role="tabpanel" id="slick-slide07" aria-describedby="slick-slide-control07">
	<div class="img"><a href="/media/web/2025/aus/AU_GrossHeide9_San_Arnts_1.jpg?1735487093" title="Ausstellung - Holz in seinen Formen" class="fancybox" rel="apics" tabindex="0"><img src="/media/web/2025/aus/AU_GrossHeide9_San_Arnts_1.jpg?1735487093" loading="lazy"></a></div>
	<div><p>Sandra Arnts<a href="/galerie/sandra-arnts-2323.html" title="Galerie anzeigen" class="star" tabindex="0"><img src="/img/fake.gif" width="18" height="17" border="0"></a></p>
		<p><b>Holz in seinen Formen</b><br><em>Objekte aus Holz und Geflecht,Vasen und schöne Kleinigkeiten aus besonders gemaserten Hölzern</em></p></div>
</div>
```
Here is the mapping of the example exhibition information:
- name: Holz in seinen Formen
- description: Objekte aus Holz und Geflecht,Vasen und schöne Kleinigkeiten aus besonders gemaserten Hölzern
- artist: Sandra Arnts
- link to artist page: /galerie/sandra-arnts-2323.html (+ base URL of the original website)
- image url: /media/web/2025/aus/AU_GrossHeide9_San_Arnts_1.jpg?1735487093 (+ base URL of the original website) -> download this image

The image can be downloaded and stored in the static folder. Make sure to only download it if it has not been downloaded yet.

Implement the list of exhibitions as a carousel on the location page, allowing users to scroll through the exhibitions at that location. Each exhibition in the carousel should display the exhibition name and description, and optionally the artist and a link to the original website for more information.
