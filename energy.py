from datetime import datetime

def input_default(prompt, default_value, auto_skip=False):
    if auto_skip:
        return default_value
    user_input = input(f"{prompt} [{default_value}]: ")
    if user_input.strip() == "":
        return default_value
    try:
        # Αν η προεπιλογή είναι float αλλά θέλουμε να τη διαχειριστούμε ως int στην είσοδο
        if isinstance(default_value, float) and default_value == 0.0:
             return float(user_input)
        return type(default_value)(user_input)
    except ValueError:
        return default_value

def ask_and_calculate_full_analysis():
    print("\n" + "="*85)
    print("      ΤΕΛΙΚΟΣ ΥΠΟΛΟΓΙΣΜΟΣ ΛΟΓΑΡΙΑΣΜΟΥ (FINAL POSITIONING & INTEGER NIGHT kWh)")
    print("="*85)
    
    date_start_str = input("Έναρξη (ΗΗ/ΜΜ/ΕΕΕΕ): ")
    date_end_str = input("Λήξη (ΗΗ/ΜΜ/ΕΕΕΕ):   ")
    
    try:
        m1_day = float(input("Παλιά ένδειξη Ημέρας kWh: "))
        m2_day = float(input("Νέα ένδειξη Ημέρας kWh:   "))
        kwh_day = m2_day - m1_day
        
        # Εισαγωγή ως int για τη νύχτα
        m1_night = input_default("Παλιά ένδειξη Νύχτας kWh", 0)
        m2_night = input_default("Νέα ένδειξη Νύχτας kWh", 0)
        kwh_night = int(m2_night) - int(m1_night)
        
        total_kwh = kwh_day + kwh_night

        use_defaults = input("\nΘέλετε να χρησιμοποιηθούν οι προεπιλεγμένες ρυθμίσεις; (ν/ο) [ν]: ").lower() != "ο"
        skip = use_defaults 

        kwh_price = input_default("Κόστος kWh Ημέρας", 0.1049, skip)
        night_kwh_price = input_default("Κόστος kWh Νύχτας", kwh_price, skip)
        fixed_fee_monthly = input_default("Κόστος Παγίου (Μηνιαίο)", 7.90, skip)
        power_kva = input_default("Ισχύς kVa (8 ή 25)", 8, skip)
        
        sq_meters = input_default("Τετραγωνικά", 87, skip)
        dt_factor = input_default("Συντ. ΔΤ (€/τμ)", 1.85, skip)
        df_factor = input_default("Συντ. ΔΦ (€/τμ)", 0.07, skip)
        tap_base_val = input_default("ΤΑΠ (Τιμή Ζώνης)", 1000, skip)
        age_factor = input_default("Παλαιότητα", 0.65, skip)
        tap_factor = input_default("Συντ. ΤΑΠ", 0.00035, skip)
        ert_yearly = input_default("ΕΡΤ (Ετήσια)", 36, skip)
        vat_rate = input_default("ΦΠΑ (%)", 6, skip) / 100
        
    except ValueError:
        print("Σφάλμα δεδομένων.")
        return

    d1 = datetime.strptime(date_start_str, "%d/%m/%Y")
    d2 = datetime.strptime(date_end_str, "%d/%m/%Y")
    days = (d2 - d1).days
    day_ratio_year = days / 365

    fixed_ch = round(fixed_fee_monthly * days / 30, 2)
    en_day_ch = round(kwh_day * kwh_price, 2)
    en_night_ch = round(kwh_night * night_kwh_price, 2)
    supply_sum = round(fixed_ch + en_day_ch + en_night_ch, 2)

    admie = round(total_kwh * 0.00999, 2)
    deddie_total = round((power_kva * 6.21 * day_ratio_year) + (total_kwh * 0.00339), 2)
    etmear = round(total_kwh * 0.017, 2)

    k1_lim = round(1600 * days / 120); k2_lim = round(400 * days / 120)
    def calc_yko(kwh, k1_l, k2_l, p1, p2, p3):
        k1 = min(kwh, k1_l); r = max(0, kwh-k1)
        k2 = min(r, k2_l); k3 = max(0, r-k2)
        return k1, k2, k3, round(k1*p1,2), round(k2*p2,2), round(k3*p3,2)

    h1,h2,h3,hv1,hv2,hv3 = calc_yko(kwh_day, k1_lim, k2_lim, 0.0069, 0.0500, 0.0850)
    n1,n2,n3,nv1,nv2,nv3 = calc_yko(kwh_night, k1_lim, k2_lim, 0.0069, 0.0150, 0.0300)
    yko_sum = round(hv1+hv2+hv3+nv1+nv2+nv3, 2)
    regulated_sum = round(admie + deddie_total + yko_sum + etmear, 2)

    efk = 1.00 
    det_base = supply_sum + regulated_sum + efk
    det_5_mil = round(det_base * 0.005, 2) 
    vat_val = round(det_base * vat_rate, 2)
    
    dt = round(sq_meters * dt_factor * day_ratio_year, 2)
    df = round(sq_meters * df_factor * day_ratio_year, 2)
    tap = round(sq_meters * tap_base_val * age_factor * tap_factor * day_ratio_year, 2)
    ert = round((ert_yearly * days) / 365, 2)

    total_bill = round(det_base + vat_val + det_5_mil + dt + df + tap + ert, 2)

    # ΕΚΤΥΠΩΣΗ
    print("\n" + "="*85)
    # Εμφάνιση kWh νύχτας ως ακέραιο
    print(f"ΑΝΑΛΥΣΗ: {days} ημέρες | {total_kwh:.0f} kWh (Νύχτα: {kwh_night:d}) | Ισχύς: {power_kva} kVA")
    print("="*85)
    # Μετακίνηση Προμήθειας και Ρυθμιζόμενων κατά 3 θέσεις δεξιά (από 12 σε 15 πλάτος)
    print(f"1. ΠΡΟΜΗΘΕΙΑ:                                  {supply_sum:15.2f} €")
    print(f"2. ΡΥΘΜΙΖΟΜΕΝΕΣ ΧΡΕΩΣΕΙΣ:                      {regulated_sum:15.2f} €")
    print(f"   ΥΚΩ [Ημέρα]: Κ1({h1:.0f}kWh):{hv1:5.2f}€ | Κ2({h2:.0f}kWh):{hv2:5.2f}€ | Κ3({h3:.0f}kWh):{hv3:5.2f}€")
    if kwh_night > 0:
        print(f"   ΥΚΩ [Νύχτα]: Κ1({n1:.0f}kWh):{nv1:5.2f}€ | Κ2({n2:.0f}kWh):{nv2:5.2f}€ | Κ3({n3:.0f}kWh):{nv3:5.2f}€")
        
    print(f"\n3. ΦΟΡΟΙ & ΔΗΜΟΣ")
    print(f"   - ΦΠΑ({vat_rate*100:.0f}%):                                   {vat_val:12.2f} €")
    print(f"   - Ε.Φ.Κ. (Σταθερό):                             {efk:12.2f} €")
    print(f"   - Ειδικό Τέλος 5‰:                              {det_5_mil:12.2f} €")
    print(f"   - ΔΤ / ΔΦ / ΤΑΠ:                                {dt+df+tap:12.2f} €")
    print(f"   - ΕΡΤ:                                          {ert:12.2f} €")
    print("="*85)
    # Μετακίνηση Τελικού Ποσού κατά 1 θέση δεξιά (από 12 σε 13 πλάτος)
    print(f"ΤΕΛΙΚΟ ΠΟΣΟ ΠΛΗΡΩΜΗΣ:                             {total_bill:13.2f} €")
    print("="*85)

if __name__ == "__main__":
    ask_and_calculate_full_analysis()
