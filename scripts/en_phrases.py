# -*- coding: utf-8 -*-
"""英文短语库。英文模型的三条提示词由此生成。

译名一经确定即全库复用：天阙永远是 the Celestial Gate。译名漂移会让
英文模型上的成套感断裂，这是本文件存在的唯一理由。
"""

# 以下三个词库一律存**裸短语**：不含「为唯一光源」「最远处」「近景」这类框架词。
# 框架词只由模板添加一次。组件自带框架词会导致模板拼出重复语句。

# 光时 -> (中文, 英文)。只给一个主光源 + 一个方向。
LIGHT = {
 '拂晓': ('拂晓逆光，日尚在山脊之下，天光自主体背后透出',
          'first light before sunrise, the sun still below the ridge, backlighting the scene from behind'),
 '正午': ('正午顶光，日在中天',
          'a high noon sun directly overhead'),
 '薄暮': ('薄暮低斜光，日将没，自画面左侧掠入',
          'a low sun minutes from setting, raking in from the left'),
 '夜':   ('夜色，月光自左上斜下',
          'moonlight from high on the left'),
}

# 下卦 -> 暗前景框装置（就近取材于下境）
FOREGROUND = {
 '乾': ('被罡风蚀过的白玉栏杆', 'a wind-scoured jade balustrade'),
 '坤': ('一道夯土矮墙', 'a rammed-earth parapet'),
 '震': ('一根焦黑的青铜柱', 'a charred bronze pillar'),
 '巽': ('几幅深色纱幡', 'dark gauze banners'),
 '坎': ('湿黑的岩石与一道水帘', 'wet black rock and a hanging water curtain'),
 '離': ('一座灯架', 'a lamp stand'),
 '艮': ('一道崖壁岩棱', 'a spur of cliff rock'),
 '兌': ('深色的荷梗与残叶', 'dark lotus stems and spent leaves'),
}

# 上卦 -> 远景消隐物（最远层，几乎化入天光）
FARFADE = {
 '乾': ('层层云头', 'banked cloud heads'),
 '坤': ('夯土层台', 'earthen tiers'),
 '震': ('最后几根焦立柱', 'the last charred posts'),
 '巽': ('最淡的一片竹影', 'the faintest stand of bamboo'),
 '坎': ('远处的一道垂瀑', 'a far cascade'),
 '離': ('几点残火', 'a few last points of lamplight'),
 '艮': ('裸露的山脊线', 'a bare ridgeline'),
 '兌': ('望不到岸的开阔水面', 'open water stretching past any shore'),
}

# 序号 -> (灵禽英文, 天候英文, 水势英文)
EN = {
1:('nine red-crowned cranes flying in formation, never landing','crystalline cloudless air','the vapour below lying flat as a mirror'),
2:('seven white deer moving slowly across the terraces, unstartled','low mist creeping over the stepped fields','bare earth, no standing water, the dust settled'),
3:('a single red-crowned crane standing motionless on broken rock','a downpour just ended, the thunderheads not yet dispersed','muddy water rising over the altar steps'),
4:('one young crane testing its footing at the spring','dense fog sealing the valley','a newborn spring seeping out from under the mountain'),
5:('two cranes halted at the water, refusing to advance','heavy cloud pressed low, the rain gathered but not yet falling','the water surface frozen still, everything waiting'),
6:('two cranes facing each other, wings half spread','high wind above meeting water vapour below','currents colliding head-on, ripples crossing'),
7:('twelve cranes standing in silent formation like troops','thick fog hiding all movement','water held beneath the earth, the surface unbroken'),
8:('nine cranes gathered in a ring, every head turned inward','the sky opened, thin cloud burnt away','water flat as a mirror, reflecting the whole realm'),
9:('a lone crane looking up, waiting for rain that will not come','dense cloud that refuses to release its rain','the bed dry, the water withdrawn'),
10:('one crane stepping carefully across the mirrored water','clear and windless','water stilled to the hardness of ice'),
11:('nine cranes passing up and down between the two realms','clear sky, vapour threading continuously between above and below','water rising through both realms'),
12:('a single crane trapped below, looking up and unable to rise','a dead layer of cloud sealing the middle, above and below cut apart','the water below run dry, nothing descending from above'),
13:('nine cranes converging on one point from every direction','clear sky, fire and heaven mirroring each other','still water reflecting one shared sky'),
14:('nine cranes circling above the golden roof','white-hot daylight, everything lit','still water throwing back the gold of the roof'),
15:('one crane bowing to drink, never lifting its neck','thin mist rising from below the mountain','low water, level, contending with nothing'),
16:('nine cranes with wings raised, on the point of calling','thunderheads breaking, light pouring through the gap','water rising with the thunder'),
17:('seven cranes following the current in single file','thin mist drifting sideways with the wind','water running with the slope, nothing held back'),
18:('one crane standing alone among ruined lotus','stagnant fog that will not lift','water rotted down to the bed, lotus collapsed into mud'),
19:('two cranes looking down at the water, their reflections beneath','the light opening, mist retreating off the water','water risen several steps, about to reach the courtyard'),
20:('a lone crane standing high on the gallery, gazing far out','mist below, the height alone clear','the water a mirror, held for the high vantage'),
21:('one crane with something gripped in its beak, neck rigid','lightning through cloud, the storm about to break','water striking the rocks, sharp and forceful'),
22:('two cranes facing their own reflections','thin mist carrying the afterglow, colouring everything','still water doubling every ornament'),
23:('one crane on steps that are beginning to give way','fine snow falling, not yet settling','water withdrawn, the foundations bared'),
24:('a single crane moving upward from deep in the earth','snow just cleared, one seam opening in the cloud','the first meltwater seeping up from below'),
25:('nine cranes startled into flight in all directions','thunder and rain arriving abruptly, cloud like a lid','water surging up brown from nowhere'),
26:('nine cranes at rest across every step, none in flight','clear and bright, the wind stopped, the cloud anchored','water held in the pool, not flowing'),
27:('two cranes pecking at something in the water','mist clean and moist enough to drink','still water clear enough to look into'),
28:('one crane on a crossbeam about to go under','high wind shaking the gallery, every banner horizontal','water over the beams, close to the roof'),
29:('a single crane standing against the current, water past its legs','unbroken rain, water arriving upon water','torrents falling tier after tier, ceaseless'),
30:('two cranes circling the flame','white-hot clear sky, not one cloud','the water burnt off, the stone bleached'),
31:('two cranes with necks crossed','mist rising off the marsh and turning back at the mountain','marsh water reaching the foot of the mountain'),
32:('two cranes standing so long they might be stone','a steady unchanging wind, cloud moving on a fixed course','the water level unchanged for years'),
33:('one crane withdrawing into the mountain shadow, half gone already','mist pouring from the mountain mouth and hiding its shape','water gone into the rock, only damp remaining'),
34:('nine cranes going straight up','high wind tearing the cloud, thunder overhead','water striking the cliff and thrown back'),
35:('nine cranes rising in formation','light spreading up from the horizon, the mist in retreat','water rising with the light over the first step'),
36:('one crane with folded wings hidden in the dark, a single white line showing','dense fog swallowing every source of light','black water giving back nothing'),
37:('five cranes gathered at one nest, large and small together','mist round the eaves with lamplight through it','the courtyard pool still, holding the lit windows'),
38:('two cranes back to back, each facing away','dense fog split down the middle, neither side reaching the other','two pools drying separately, never meeting'),
39:('one crane caught to its body in the frozen water','packed snow closing the road, wind carrying grains of ice','the water frozen solid, motionless'),
40:('nine cranes opening their wings and flying out of the gorge','the storm just ended, the cloud splitting open','ice breaking, water running hard'),
41:('a lone crane standing on the mark the water left','mist thinning, the air giving something up','water withdrawn, leaving band after band of old tideline'),
42:('nine cranes descending to receive it, wings slightly open','fine rain, soundless','water rising slowly, reaching the roots'),
43:('nine cranes flying hard to escape the water','high wind ripping the cloud, light straight down','a breached bank, water pouring across'),
44:('one crane meeting a single dark bird it did not expect','wind starting at floor level, the hanging banners just stirring','one fine line opening across the still water'),
45:('twelve cranes massed in one place, too many to count','clear sky, the air washed','water pooling and rising'),
46:('one crane spiralling upward, higher with each turn','mist rising through the columns from below','water climbing the steps one level at a time'),
47:('one crane trapped in the dry marsh, wings hanging','dense fog pressing down, no way out','the marsh bed cracked, not a drop left'),
48:('one crane bending to drink from the well','mist over the wellmouth, air rising out of the shaft','well water deep and unmoving, clear enough to mirror a face'),
49:('five cranes moulting, old feathers on the water','the wind changing direction, the cloud turning over','water and fire cancelling, the level dropping fast'),
50:('two cranes stationed either side of the vessel like guards','clear, with cooking smoke going straight up','still water, the vessel reflected without a tremor'),
51:('twelve cranes flushed up across the whole realm','lightning and thunder together, wind tearing the banners','the water shattering inch by inch'),
52:('one crane on a single leg, unmoved for a long time','clear, the wind entirely stopped, no dust moving','the water absolutely unrippled, as if set'),
53:('seven cranes climbing the stair in strict order','mist withdrawing layer by layer','water crossing the steps one level at a time, pausing at each'),
54:('two cranes, one ahead and one behind, never abreast','thin mist taking the afterglow, the colour warm','still water holding two figures in file'),
55:('twelve cranes at full number, filling the realm','clear, the light so strong that nothing casts a side shadow','the water full and level, at its height'),
56:('one crane passing straight through, wings still spread','mist far off, the near air clear','water too shallow to stay in'),
57:('nine cranes gliding downwind, wings motionless','a long wind through the gallery, every banner laid flat','the water pressed dead flat by the wind'),
58:('nine cranes playing in the water, spray thrown up','clear, the light broken across the surface','two marshes joined, their waters continuous'),
59:('nine cranes scattering, no two on the same heading','high wind driving apart everything that had gathered','water pushed apart, ripples radiating outward'),
60:('two cranes stationed either side of the divide','clear, each cloud keeping its own boundary','the water standing exactly at the marked level'),
61:('three cranes, one adult and two chicks, calling and answering','mist over the marsh carrying the sound','still water in which the sound seems visible'),
62:('one crane flying low across the ridge, never rising high','high wind skimming the ridgeline, cloud low and fast','the water barely rippled, crossed but not entered'),
63:('nine cranes each in its own position, evenly spaced','even mist, neither element dominant','water level matched to fire level, each in place'),
64:('one young crane crossing, its tail dragging wet','fog not yet lifted, the way ahead unreadable','water fast and not yet fordable'),
}
