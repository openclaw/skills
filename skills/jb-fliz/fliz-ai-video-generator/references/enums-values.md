# Fliz API Enum Values

Complete list of all valid enum values for Fliz API parameters.

## Video Format (`format`)

```
size_16_9   → Landscape 16:9 (YouTube, websites)
size_9_16   → Portrait 9:16 (TikTok, Reels, Shorts)
square      → Square 1:1 (Instagram, Facebook)
```

## Video Category (`category`)

```
article     → Blog posts, news articles (default)
product     → Product showcase (requires image_urls)
ad          → Advertisement (requires image_urls)
```

## Script Style (`script_style`)

```
classified_ad                       → Classified ad format
cooking_recipe                      → Recipe/cooking format
ecommerce_commercial_presentation   → E-commerce product showcase
ecommerce_product_test              → Product test/review format
health_wellness                     → Health & wellness content
history_culture                     → Historical/cultural content
news_narrative_podcast_style        → Podcast narrative style
news_social_media_style             → Social media optimized (default)
news_tv_style                       → TV news format
news_youtube_educational_style      → YouTube educational
psychology_personal_development     → Personal development
real_estate_listing                 → Real estate listing
science_future                      → Science & technology
step_by_step_tutorial               → Tutorial format
story_children                      → Children's story
story_paranormal                    → Paranormal/mystery story
```

## Image Style (`image_style`)

```
african_pattern              → African geometric patterns
australian_aboriginal_art    → Aboriginal dot art style
brazilian_cordel_art         → Brazilian woodcut style
charcoal                     → Charcoal drawing
classic_american_animation   → Classic Disney-style
classic_cartoon_1            → Cartoon style variant 1
classic_cartoon_2            → Cartoon style variant 2
classical_painting           → Renaissance/classical art
clay_animation               → Claymation style
color_pencil                 → Colored pencil drawing
comic_book                   → Comic book illustration
creative_collage             → Collage art style
cut_out_sticker              → Paper cutout style
cuteyukimix                  → Cute anime style
cyber_fantasy                → Cyberpunk fantasy
dark_cinematography          → Dark cinematic look
dark_digital                 → Dark digital art
dark_fantaisy                → Dark fantasy style
digital_art                  → Modern digital art
experimental_photography     → Experimental photo style
fantasy                      → Fantasy illustration
fine_art_monochrome          → Black & white fine art
future_vision                → Futuristic vision
futurism                     → Futurist art movement
horror                       → Horror style
hyperrealistic               → Photorealistic (default)
indigenous_amazonian_art     → Amazonian tribal art
ink_art                      → Ink illustration
japan_sumi_e_ink             → Japanese ink wash
japanese_animation           → Anime style
japanese_horror              → J-horror style
japanese_woodblock_print     → Ukiyo-e style
kawaii                       → Cute Japanese style
manga                        → Manga illustration
marker_art                   → Marker drawing
mexican_painting             → Mexican folk art
minimalist                   → Minimalist design
modern_gaming                → Video game style
neo_pop                      → Neo-pop art
neon_glow                    → Neon aesthetic
persian_art                  → Persian miniature
pixel_art                    → 8-bit pixel style
pop_art_1                    → Pop art variant 1
pop_art_2                    → Pop art variant 2
propaganda_style             → Propaganda poster
psychedelic_vision           → Psychedelic art
retro_gaming                 → Retro video game
retro_nostalgia              → Vintage/retro style
seventies_vibe               → 1970s aesthetic
silhouette_art               → Silhouette style
stick_figure_drawing         → Simple stick figures
storybook_1                  → Storybook style 1
storybook_2                  → Storybook style 2
storybook_3                  → Storybook style 3
style_3d_animation           → 3D rendered style
tarot_cards                  → Tarot card style
traditional_indian           → Traditional Indian art
vintage_decay                → Vintage distressed
vintage_illustration         → Vintage illustration
vintage_tattoo               → Traditional tattoo
watercolor                   → Watercolor painting
wool_felt_art                → Felt/textile art
```

## Caption Style (`caption_style`)

```
animated_background    → Animated highlight background (default)
bouncing_background    → Bouncing text animation
colored_words          → Colored word emphasis
scaling_words          → Scaling text animation
```

## Caption Position (`caption_position`)

```
bottom    → Bottom of screen (default)
center    → Center of screen
```

## Caption Font (`caption_font`)

```
cabin       → Cabin font
inter       → Inter font
lato        → Lato font
montserrat  → Montserrat font
nunito      → Nunito font
open_sans   → Open Sans font
oswald      → Oswald font
poppins     → Poppins font (default)
roboto      → Roboto font
ubuntu      → Ubuntu font
```

## Video Step (`step`) - Status Values

### Processing Steps (in order):
```
pending                 → Queued for processing
scrapping               → Extracting content
meta                    → Processing metadata
script                  → Generating script
image_prompt            → Creating image prompts
image_script            → Processing image script
image_generation        → Generating AI images
image_analysis          → Analyzing images
image_to_video          → Converting images to video
speech                  → Generating voiceover
transcribe              → Creating transcript
fix_transcribe          → Fixing transcription
translation             → Translating content
video                   → Assembling video
video_rendering         → Final rendering
video_rendering_queue   → In rendering queue
```

### Final States:
```
complete                        → ✅ Video ready (url field populated)
failed                          → ❌ Recoverable error
failed_unrecoverable            → ❌ Permanent failure
failed_go_back_to_user_action   → ⚠️ Needs user correction
user_action                     → ⚠️ Manual intervention required
block                           → ⛔ Processing blocked
```

## Video Animation Mode (`video_animation_mode`)

```
full_video    → Animate entire video (default)
hook_only     → Only animate the hook/intro
```

## Language Codes (`lang`)

ISO 639-1 codes. Common values:
```
en → English
fr → French
es → Spanish
de → German
it → Italian
pt → Portuguese
nl → Dutch
pl → Polish
ru → Russian
ja → Japanese
ko → Korean
zh → Chinese
ar → Arabic
hi → Hindi
tr → Turkish
vi → Vietnamese
th → Thai
id → Indonesian
```
