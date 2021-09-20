ALTER TABLE public.ax_gebaeude ADD COLUMN use VARCHAR;

UPDATE public.ax_gebaeude 
SET use = 'Residential' WHERE gebaeudefunktion::text LIKE '%10__';

UPDATE public.ax_gebaeude 
SET use = 'Mixed use' WHERE gebaeudefunktion::text LIKE '%11__';

UPDATE public.ax_gebaeude 
SET use = 'Agroforestry' WHERE gebaeudefunktion::text LIKE '%12__';

UPDATE public.ax_gebaeude 
SET use = 'Leisure' WHERE gebaeudefunktion::text LIKE '%13__';

UPDATE public.ax_gebaeude 
SET use = 'Commercial' WHERE gebaeudefunktion::text LIKE '%20__';

UPDATE public.ax_gebaeude 
SET use = 'Industrial' WHERE gebaeudefunktion::text LIKE '%21__';

UPDATE public.ax_gebaeude 
SET use = 'Miscellaneous commercial/industrial' WHERE gebaeudefunktion::text LIKE '%22__';

UPDATE public.ax_gebaeude 
SET use = 'Commercial plus residential' WHERE gebaeudefunktion::text LIKE '%23__';

UPDATE public.ax_gebaeude 
SET use = 'Transport-related' WHERE gebaeudefunktion::text LIKE '%24__';

UPDATE public.ax_gebaeude 
SET use = 'Infrastructure' WHERE gebaeudefunktion::text LIKE '%25__';

UPDATE public.ax_gebaeude 
SET use = 'Waste management' WHERE gebaeudefunktion::text LIKE '%26__';

UPDATE public.ax_gebaeude 
SET use = 'Agroforestry' WHERE gebaeudefunktion::text LIKE '%27__';

UPDATE public.ax_gebaeude 
SET use = 'Public/Administrative' WHERE gebaeudefunktion::text LIKE '%30__';

UPDATE public.ax_gebaeude 
SET use = 'Public plus residential' WHERE gebaeudefunktion::text LIKE '%31__';

UPDATE public.ax_gebaeude 
SET use = 'Leisure' WHERE gebaeudefunktion::text LIKE '%32__';

UPDATE public.ax_gebaeude 
SET use = 'Unknown' WHERE gebaeudefunktion = 9998;










