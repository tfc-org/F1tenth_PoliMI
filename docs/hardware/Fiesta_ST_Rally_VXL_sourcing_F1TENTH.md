# Traxxas Fiesta ST Rally VXL: Sourcing for the F1TENTH Build

*Last updated: 24 September 2026*

## Brief

Our Master BOM chassis line is the **Traxxas Ford Fiesta ST Rally VXL (model 74276-4)**. The Traxxas landing page no longer shows a price. This document covers two routes:

1. **Plan A:** buy the complete car from a vendor that ships to Italy within a month.
2. **Plan B:** buy only the Traxxas parts the F1TENTH/RoboRacer build actually keeps, and assemble a rolling chassis from spare parts.

The Master BOM (`hardware/bom/Master BOM.xlsx`) was read but **not modified**.

### How missing information is marked

| Tag | Meaning |
|---|---|
| **[MISSING]** | Couldn't be found or read from the available sources. Must be filled in before ordering. |
| **[VERIFY]** | Best guess from indirect evidence. Check it against the Traxxas exploded views or a physical car before ordering. |
| **[BOM GAP]** | Something the build needs that isn't in our Master BOM. |

---

## 1. Status of the complete car

- **Traxxas.com:** the model page for 74276-4 is still online, but no price is shown (the page metadata says "$0"). No "in stock" or "add to cart" option is visible.
- **Wheelspin Models (UK):** *"Sorry, this item is discontinued and no longer available."*
- **Conclusion:** the 74276-4 appears to be **end-of-life** and only leftover retail stock remains. **[VERIFY]** We don't have official confirmation from Traxxas that it's discontinued.

---

## 2. Plan A: vendors that ship to Italy

Stock status was read from each product page on **24 Sep 2026**. It can change daily, so check again before ordering.

| # | Vendor (country) | Price | Stock text on page | Ships to Italy? | Delivery estimate | Verdict |
|---|---|---|---|---|---|---|
| 1 | [evocrc.com](https://www.evocrc.com/rallye/145037-ford-fiesta-st-rally-vert-brushless-vxl-3s-rtr-traxxas-74276-4-grn-110.html) (FR), green | **€509.90** | "Dernier article" (**last unit** in stock) | **Yes**, EU rate €12.90–15.90 | **[MISSING]** EU transit time not stated. French tracked shipping to Italy usually takes about 3–7 days. | **Best bet. It's in stock and ships to Italy. Order now.** |
| 2 | [Rueil Modélisme](https://rueil-modelisme.com/electrique-tt-pret-a-rouler/7155-ford-fiesta-st-rally-vxl-id-rtr-74276-4-traxxas.html) (FR) | €509.90 | In stock ("Livraison en 48H", France) | **[MISSING]**, not stated. Ask them at rm-infos@wanadoo.fr or +33 1 47 77 08 88. | 48 h in France. Italy **[MISSING]**. | Backup if evocrc sells out. Email them first. |
| 3 | [EuroRC](https://www.eurorc.com/product/37190/traxxas-ford-fiesta-st-rally-110-vxl-4x4-brushless-rtr) (DK), green and orange | €499.95 | **Backorder**, "estimated delivery time 14 days" | Yes (ships to 180+ countries; UPS from €16.90) | About 14 days plus 1–7 days shipping. **[VERIFY]** A backorder date on an EOL model may slip. | Fits the one-month window only if the backorder date holds. |
| 4 | [Jetmodel](https://www.jetmodel.it/prodotto/traxxas-74276-4-ford-fiesta-st-rally-4wd-110-brushless-vxl-3s-tqi-2-4ghz-tsm-rtr/) (IT) | €479.00 | "Disponibile su ordinazione" (**to order**) | Yes (domestic) | **[MISSING]** No lead time given | Cheapest, but ask for a firm date before paying. |
| 5 | [Modellismo.it](https://www.modellismo.it/visualizza_oggetto.php?cod=TXX74276-4-GRN&dove=%2Fprodotti%2Ftraxxas&lingua=ita) (IT), green | €479.90 | **[MISSING]**, "request availability" (assistenza@modellismo.it) | Yes, free shipping | **[MISSING]** | Worth an email. It's domestic with free shipping. |

**Checked but not usable:** Modelsport UK (no stock data), Wheelspin UK (discontinued), promodelisme67.fr (page removed), mrcmodelisme.fr (page removed), eBay.de listing (*"momentan ausverkauft"*, sold out). Several Italian shops couldn't be read automatically (Pieroni Modellismo returned an error, Modellismo Gianni blocks crawlers, D.P. Modellismo and ModelsportRC returned 404). **[MISSING]** Check these by hand:

- [Pieroni Modellismo, VXL](https://www.pieronimodellismo.it/traxxas-74276-4-ford-fiesta-st-rally-4wd-110-brushless-vxl-3s-tqi-24ghz-tsm-rtr-7506.html)
- [Modellismo Gianni, orange](https://www.modellismogianni.it/products/TXX74276-4ORG_ford-fiesta-st-arancione-rally-oltre-96km-h-vxl-3s-1-10-4wd-brushless-traxxas.php) and [green](https://www.modellismogianni.it/products/TXX74276-4GRN_ford-fiesta-st-verde-rally-oltre-96km-h-vxl-3s-1-10-4wd-brushless-traxxas.php)

**Colour doesn't matter:** we throw the body away, so green (-GRN) and orange (-ORNG) are equivalent for us.

### Plan A fallbacks if no 74276-4 can be found

| Option | Why it could work | Caveat |
|---|---|---|
| **Slash 4x4 VXL Ultimate** (68277-4) | Our BOM already lists it as compatible with the platform deck. It's also the chassis the RoboRacer guide is written for. | More expensive: $529.95 per our BOM comment. EU price **[MISSING]**. |
| **Fiesta ST Rally BL-2s** (74154-4) | Same body and chassis family. Listed at [Pieroni](https://www.pieronimodellismo.it/traxxas-ford-fiesta-st-rally-4wd-110-brushless-bl-2s-tq-24ghz-rtr-7361.html). | Comes with the BL-2s brushless system, not the Velineon 3500. It also doesn't have the Extreme Heavy Duty parts. **[VERIFY]** Check whether its motor suits the VESC and 3S, or budget for a Velineon 3500 (#3351R). |

---

## 3. What the RoboRacer build keeps and what it throws away

### Source and an important caveat

The official build guide ([f1tenth_doc, `getting_started/build_car/`](https://github.com/f1tenth/f1tenth_doc/tree/main/getting_started/build_car), rendered at [f1tenth.readthedocs.io](https://f1tenth.readthedocs.io/)) is **written for the Traxxas Slash 4x4 Premium**, which has a brushed Titan motor and an XL-5 ESC. The Rally VXL only shows up in the BOM spreadsheet, and the guide calls its old "Ford Fiesta" section "DEPRECATED". The table below applies the guide's logic to the Rally VXL's actual parts, using the [74276-4 parts list (REV. 260209)](https://traxxas.com/media/productattach/C-74276-4/3/74276-4_parts.pdf).

| Guide step (Slash 4x4) | What it means on the Fiesta ST Rally VXL |
|---|---|
| "Remove the four Body Clips to remove the Body" | The Rally has a **clipless** body (#7420 and #7414). The body and all its trim are **discarded**. |
| Remove the **XL-5 ESC** | Remove the **VXL-3s ESC (#3355R)**. The **VESC 6 MkVI** replaces it. **Discarded.** |
| Remove the **receiver box** and receiver | Remove the **receiver box (#7424)** and the **TQi receiver (#6533)**. **Discarded.** The joystick and Jetson replace the radio. |
| Remove the **antenna tube** | #1726 and #1926. **Discarded.** |
| Remove the **brushed motor** and fit the BOM brushless motor | **Not applicable.** The VXL already has a **Velineon 3500 brushless motor (#3351R)**, and it's **KEPT**. Our Master BOM has no motor line, which matches. The BOM's 4 mm-to-3.5 mm bullet adapters exist to connect this motor to the VESC. |
| "The only component which we will not be removing is the **Servo**" | The **2075 servo** is **KEPT**. The VESC drives it through the PPM cable. |
| Remove the "plastic fork" / **Battery Hold-Down** | **#7426: discarded.** The battery sits under the platform deck. |
| Remove the two **Nerf Bars** (and reuse their M3 screws) | **Not applicable / [VERIFY]**. The Rally parts list has no nerf bars. The guide reuses those screws later, so source M3 screws from the BOM's M3 kit instead. |
| Fit three **45 mm M3 standoffs** into the chassis (two on the motor side, one on the battery side) | Uses chassis #7422. **[VERIFY]** Our BOM says the platform deck fits the Rally, but the guide shows hole positions for the Slash Premium chassis. #7422 is the "Slash **LCG** and Rally" chassis, so check the hole alignment on the real part or in CAD. |
| Motor to VESC: three **4 mm to 3.5 mm bullet adapters** | Keep the motor's 3.5 mm bullets. The adapters are already in the BOM. |
| Battery to VESC through a **TRX to XT90 adapter** | **[BOM GAP]** Our BOM has no TRX (Traxxas High-Current) to XT90 adapter. The Trampa VESC has XT90 connectors. Also check which connector the Zeee 6000 mAh 3S packs ship with (**[MISSING]**). |

### Kept vs discarded, by subsystem

**KEPT (the "rolling chassis", plus motor and servo):**

- Chassis tub, bulkheads, tie bars, skidplate, gear cover
- Complete 4WD driveline: front and rear sealed diffs, center slipper clutch, center driveshaft, front and rear half-shafts, spur and pinion, motor mount and plate
- Suspension: arms, pins, caster blocks, steering blocks, stub-axle carriers, shock towers, camber and toe links, Ultra Shocks
- Steering: bellcranks, servo saver, drag link, front toe links, **2075 servo**
- Wheels, tyres, hubs, bearings, wheel nuts
- **Velineon 3500 motor**

**DISCARDED (not needed, or replaced by F1TENTH parts):**

- Body and all body accessories: body (7427-x), clipless mounts (7420), cross brace (7414), front reinforcement and body posts (7410), wing (7413X), side trim (7419), decals
- Receiver box (7424), its seal kit (7425) and access plug (3698)
- Battery hold-down (7426)
- Antenna tube and caps (1726, 1926)
- VXL-3s ESC (3355R), its BEC (2260) and fan (3340)
- TQi transmitter and receiver (6509R, 6528, 6533), plus the telemetry sensors
- Included AA batteries and tools, if you're buying parts (see the tools note below)

---

## 4. Plan B: Traxxas individual-parts list

### Read this first

1. **Where to buy:** Traxxas's own parts web pages (traxxas.com/parts-finder) couldn't be read by the tools used here, and **[MISSING / VERIFY]** we don't know whether traxxas.com ships spare parts to Italy (it has historically been US-focused). The part numbers below are universal Traxxas codes, so EU shops sell them under the same number, usually prefixed "TRX" or "TXX". EuroRC and the Italian shops above all carry Traxxas spares.
2. **Prices:** where given, prices are **USD from [HobbyQuarters' Fiesta ST Rally VXL parts listing](https://www.hobbyquarters.com/rc-vehicles/vehicles-by-brand/traxxas-vehicles/traxxas-parts/traxxas-parts-by-vehicle/ford-fiesta-st-rally-vxl-parts/)** (US retailer). They're **indicative only**; EU prices will differ. "—" = **[MISSING]**.
3. **Stock vs optional:** the Traxxas parts list says *"Parts shown in bold are optional accessories"*, but that formatting was lost when the PDF was read. Where a part comes in several colours or materials, the plain black or composite version was picked as the likely stock part and marked **[VERIFY]**. Confirm against the **exploded views** in the 74276-4 support section on traxxas.com.
4. **Screws and bearings:** a factory car comes fully screwed together, but spare parts often don't include hardware. Exact screw and bearing **quantities per location are [MISSING]**. They can only come from the exploded views.

### 4.1 Chassis and structure

| Qty | Part # | Description | Stock? | Price (USD, indicative) | Notes |
|---|---|---|---|---|---|
| 1 | **7422** | Chassis, Slash LCG / Rally | Stock | $20.00 | This is where the platform-deck standoffs go. **[VERIFY]** Check the hole pattern. |
| 1 | **7430X** | Bulkhead, front | Stock | $6.99 | |
| 1 | **7429** | Bulkhead, rear | Stock | — | |
| 1 | **6823** (or -G / -ORNG / -R) | Bulkhead tie bars, front & rear, aluminium | **[VERIFY]** Stock colour unknown | — | |
| 1 | **7435** | Front skidplate, angled | Stock | $4.99 | |
| 1 | **7477** | Gear cover with wire retainer | Stock | — | Keep it. It guards the spur gear against cables. |
| 1 | 7434 | Foam body bumper, low profile (goes with 7435) | Stock | — | **Recommended.** F1TENTH cars hit walls. |
| — | 6730X / G / A / R | Chassis brace kit, 4X4 Low-CG | **[VERIFY]** Probably optional | — | Leave it out unless the exploded view shows it on the stock car. |

### 4.2 Driveline

| Qty | Part # | Description | Stock? | Price | Notes |
|---|---|---|---|---|---|
| 1 | **6788** | Front differential, complete (13/37, rally) | Stock | — | Comes as a complete assembly. |
| 1 | **6789** | Rear differential, complete (13/37, rally) | Stock | — | Comes as a complete assembly. |
| 1 | **6878** | Slipper clutch, complete | Stock | $20.99 | The Rally VXL has a center **slipper clutch, not a center diff** (#6780 is optional). |
| 1 | **6893R** | Slipper input shaft with bearing adapter and pin | Stock | — | **[VERIFY]** Check whether 6878 already includes it. |
| 1 | **6888** | Center rear drive hub | Stock | — | |
| 1 | **6888X** | Front drive hub, hardened steel | Stock | — | |
| 1 | **7455** | Center driveshaft, plastic (black) | **[VERIFY]** | $4.99 | 6855 (aluminium, 214 mm) is the upgrade. |
| 2 | **7450** | Front half-shaft assembly, Extreme HD, 6 mm axle | Stock | $14.99 each | **[VERIFY]** Retailer lists it as "left **or** right", so 2 needed. |
| 2 | **7451** | Rear half-shaft assembly, Extreme HD, 6 mm axle | Stock | $14.99 each | Same as above. |
| 1 | **6842** | Spur gear, 50T, 0.8 metric pitch | **[MISSING]** Stock tooth count unknown (50, 52 or 54T) | — | The owner's manual gearing chart has the stock ratio. |
| 1 | **Pinion [MISSING]** | 32-pitch steel pinion, 3 mm bore | **[MISSING]** Stock tooth count unknown | 12T 3942X: $5.99 | The manual says an optional "large pinion" ships in the box. For indoor F1TENTH speeds, the smaller stock pinion is usually preferred. |
| 1 | **7460A** | Motor mount with 3x6 flat-head screw and nylock nut | Stock | — | |
| 1 | **7490** (or G / A / R) | Motor plate | **[VERIFY]** Stock colour | $7.99 (7490R) | |

### 4.3 Suspension

| Qty | Part # | Description | Stock? | Price | Notes |
|---|---|---|---|---|---|
| 2 | **6731** | Suspension arms, front/rear L&R (2 per pack) | Stock | $10.00 each | 4 arms in total. |
| 1 | **9042** | Suspension pin set, Extreme HD, complete (front & rear) | Stock (9042X = hardened upgrade) | — ($15.99 for 9042X) | |
| 1 | **9032** | Caster blocks (C-hubs), Extreme HD, black | **[VERIFY]** Stock colour | $7.00 (gray variant) | |
| 1 | **9037** | Steering blocks, Extreme HD, black, L&R | **[VERIFY]** Stock colour | $6.99 (gray variant) | |
| 1 | **9050** | Rear stub-axle carriers, Extreme HD, black | **[VERIFY]** Stock colour | — | |
| 1 | **9038** | Front shock tower, Extreme HD, black | **[VERIFY]** Stock colour | $6.99 | |
| 1 | **9039** | Rear shock tower, Extreme HD, black | Stock | $6.99 | |
| 1 | **7432** | Camber links, 49 mm (72 mm c-c), front | Stock | $8.99 | **[VERIFY]** Front/rear assignment |
| 1 | **7431** | Camber links, 49 mm (63 mm c-c), rear | Stock | $8.99 | **[VERIFY]** Front/rear assignment |
| 1 | **7433** | Toe links, 47 mm (77 mm c-c), rear | Stock | $8.00 | **[VERIFY]** |
| 1 | **3760A** | Ultra Shocks, gray, long, complete with springs (front, pair) | **[VERIFY]** | — | The manual refers to Ultra Shocks and rebuild kit #2362. GTR and Big Bore shocks are optional. |
| 1 | **3762A** | Ultra Shocks, gray, XX-long, complete with springs (rear, pair) | **[VERIFY]** | $18.99 | |
| 1 | **5529** | Shim set / hollow balls | Stock | — | |
| 1 | **2742** | Rod ends, long (6) / hollow balls (6) | Stock | — | |

### 4.4 Steering (servo KEPT)

| Qty | Part # | Description | Stock? | Price | Notes |
|---|---|---|---|---|---|
| 1 | **2075** | Digital high-torque waterproof servo | Stock | — | **Kept by the F1TENTH build.** It's connected to the VESC through the PPM cable. |
| 1 | **6845X** | Bellcranks, servo saver, spring, retainer, servo horn | Stock | — | |
| 1 | **7438** | Drag link (steering linkage) | Stock | — | 6845A (aluminium) is the upgrade. |
| 1 | **7439** | Front toe links, composite (2), with hollow balls | Stock | $5.99 | |
| 1 | **2545** | Bellcrank bushings, 5x8x2.5 mm (4) | Stock | $3.00 | |
| — | **[MISSING]** | Servo mounting screws and posts | — | — | Not a separate line in the parts list. Probably covered by the chassis and hardware packs. Check the exploded view. |

### 4.5 Wheels and hubs

| Qty | Part # | Description | Stock? | Price | Notes |
|---|---|---|---|---|---|
| 2 | **7473** (or 7473T / X / A / GRAY) | Tyres & wheels, assembled and glued, gravel pattern (2 per pack) | **[VERIFY]** Stock wheel colour | $24.99 each | Gravel tyres grip poorly on smooth indoor floors. Consider road tyres. **[MISSING]** No compatible on-road Traxxas part number was researched. |
| 1 | **9069** | Wheel hubs, 12 mm hex, steel, Extreme HD, with pins | Stock | $10.99 | |
| 1 | **2754** | Stub-axle pins (4) | Stock | — | |
| 1 | **3647** | Wheel nuts, 4 mm flanged nylock, serrated (8) | **[VERIFY]** (1747 is the alternative) | — | |
| 1 | 5854 | Hub retainer, 17 mm, M4 (4) | **[VERIFY]** Whether it's used on this model | $8.99 | |

### 4.6 Motor (KEPT)

| Qty | Part # | Description | Stock? | Price | Notes |
|---|---|---|---|---|---|
| 1 | **3351R** | Velineon 3500 brushless motor, with 3.5 mm bullet connectors | Stock | — | Kept and driven by the VESC. As an alternative, the **3350R** combo (motor + ESC + plate, $189.99) is sometimes easier to find. You'd then throw away the ESC. |

### 4.7 Bearings: quantities [MISSING]

Every rotating part in the list above needs bearings, and the spare assemblies mostly come without them. The model uses these sizes (blue rubber-sealed, 2 per pack):

| Part # | Size | Where it's likely used |
|---|---|---|
| 5116 | 5x11x4 mm | Slipper and center driveline |
| 5117 | 6x12x4 mm | Differentials and axles |
| 5118 | 8x16x5 mm | Differentials |
| 5119 | 10x15x4 mm | Driveline and differentials |
| 5120 | 12x18x4 mm | Driveline |
| 1985 | 5x8x0.5 mm PTFE washers (20) | Various |

**[MISSING]** Quantity of each bearing. Count them from the exploded views before ordering.

### 4.8 Hardware: quantities [MISSING]

The main screw families on this model (all hex drive, packs of 6): button-head 3x6 (2575), 3x8 (2576), 3x10 (2577), 3x12 (2578), 3x15 (2579), 3x18 (2583), 3x20 (2580), 3x23 (2591), 3x30 (2582), 3x40 (2592); cap-head 2.5x6 (3215), 2.5x8 (3965), 3x8 (1552), 3x15 (2586); flat-head 3x6 (3932), 3x8 (3931), 3x15 (3646); countersunk 3x6 (2534), 3x12 (2552), 4x12 (2542), 4x15 (2546); button-head 4x10/12/14 (3936/3937/3938); nylock nuts 3 mm (2745) and 4 mm (1747); grub screws (2743); washers 3x6 (2746); shock shoulder screws (3642X).

**[MISSING]** How many of each go on the car. This is the biggest risk in Plan B: one missing screw stops the build.

### 4.9 Tools (included in the RTR box, NOT with spare parts)

The RoboRacer guide relies on *"the three hex keys (M3, M2.5, M2) included in the TRAXXAS kit"*. If you buy parts, add a hex driver set, for example Traxxas **2748R** (tool set) or **8712** (Speed Bit Essentials). You can also use any quality 1.5 / 2.0 / 2.5 mm hex drivers plus a 4 mm / 7 mm nut driver. Price **[MISSING]**.

### 4.10 Cost picture

- **Known-price lines only** (23 of about 45 lines, US retailer prices, using the stated variants): **about $304**.
- **Not yet priced (the expensive items):** the Velineon 3500 motor (3351R), the 2075 servo, two complete differentials (6788 and 6789), front and rear Ultra Shocks (3760A), slipper parts, all bearings and all hardware. All **[MISSING]**.
- Even before those items, Plan B is heading toward or above the **€480–510 price of the complete RTR car**. It also needs a full assembly job with missing-hardware risk.

---

## 5. Recommendation

1. **Buy the complete car now (Plan A).** evocrc.com had its **last unit** at €509.90 with EU shipping of €12.90–15.90, and it's the only listing confirmed both **in stock** and **shipping to Italy**. If it's gone, email Rueil Modélisme (in stock, Italy shipping unconfirmed), then Modellismo.it and Jetmodel for a firm date. Use EuroRC's 14-day backorder only if you get a confirmed date.
2. **Use Plan B only if Plan A fails.** Before ordering, fill in the **[MISSING]** bearing and hardware counts from the Traxxas exploded views, and confirm the stock colour and variant lines marked **[VERIFY]**.
3. Whichever plan you choose, fix the **[BOM GAP]**: add a **TRX (Traxxas High-Current) to XT90 adapter**, and check the Zeee battery connector against the VESC's XT90.

---

## Sources

- [Traxxas: Ford Fiesta ST Rally VXL product page](https://traxxas.com/products/landing/fiesta-st-rally-vxl/)
- [Traxxas: 74276-4 parts list PDF (REV. 260209)](https://traxxas.com/media/productattach/C-74276-4/3/74276-4_parts.pdf)
- [Traxxas: 74276-4 owner's manual](https://traxxas.com/media/productattach/C-74276-4/2/74276-4-OM-EN-R01.pdf)
- [RoboRacer / F1TENTH build docs (GitHub source)](https://github.com/f1tenth/f1tenth_doc/tree/main/getting_started/build_car): `lower_level_chassis.rst`, `all_together.rst`, `upper_level_chassis.rst`, `bom.rst`
- [HobbyQuarters: Fiesta ST Rally VXL parts (indicative USD prices)](https://www.hobbyquarters.com/rc-vehicles/vehicles-by-brand/traxxas-vehicles/traxxas-parts/traxxas-parts-by-vehicle/ford-fiesta-st-rally-vxl-parts/)
- Vendors: [evocrc](https://www.evocrc.com/rallye/145037-ford-fiesta-st-rally-vert-brushless-vxl-3s-rtr-traxxas-74276-4-grn-110.html), [Rueil Modélisme](https://rueil-modelisme.com/electrique-tt-pret-a-rouler/7155-ford-fiesta-st-rally-vxl-id-rtr-74276-4-traxxas.html), [EuroRC](https://www.eurorc.com/product/37190/traxxas-ford-fiesta-st-rally-110-vxl-4x4-brushless-rtr), [Jetmodel](https://www.jetmodel.it/prodotto/traxxas-74276-4-ford-fiesta-st-rally-4wd-110-brushless-vxl-3s-tqi-2-4ghz-tsm-rtr/), [Modellismo.it](https://www.modellismo.it/visualizza_oggetto.php?cod=TXX74276-4-GRN&dove=%2Fprodotti%2Ftraxxas&lingua=ita), [Wheelspin Models](https://wheelspinmodels.co.uk/i/traxxas-rally-vxl-ford-fiesta-st-363135/)
