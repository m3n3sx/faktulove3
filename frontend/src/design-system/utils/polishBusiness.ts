/**
 * Polish Business Utilities
 * Utilities for Polish business logic, validation, and formatting
 */

// Polish currency formatting
export const formatPolishCurrency = (amount: number, currency: string = 'PLN'): string => {
  const formatter = new Intl.NumberFormat('pl-PL', {
    style: 'currency',
    currency: currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
  
  return formatter.format(amount);
};

// Parse Polish currency string to number
export const parsePolishCurrency = (value: string): number => {
  // Remove currency symbols and normalize
  const normalized = value
    .replace(/[^\d,.-]/g, '') // Remove non-numeric characters except comma, dot, minus
    .replace(/\s/g, '') // Remove spaces
    .replace(',', '.'); // Replace comma with dot for parsing
  
  return parseFloat(normalized) || 0;
};

// NIP validation using checksum algorithm
export const validateNIP = (nip: string): boolean => {
  // Remove any formatting
  const cleanNip = nip.replace(/[^0-9]/g, '');
  
  // Must be exactly 10 digits
  if (cleanNip.length !== 10) {
    return false;
  }
  
  // Cannot be all zeros
  if (cleanNip === '0000000000') {
    return false;
  }
  
  // Calculate checksum
  const weights = [6, 5, 7, 2, 3, 4, 5, 6, 7];
  let sum = 0;
  
  for (let i = 0; i < 9; i++) {
    sum += parseInt(cleanNip[i]) * weights[i];
  }
  
  const checksum = sum % 11;
  const lastDigit = parseInt(cleanNip[9]);
  
  return checksum === lastDigit;
};

// Format NIP with dashes
export const formatNIP = (nip: string): string => {
  const cleanNip = nip.replace(/[^0-9]/g, '');
  
  if (cleanNip.length === 10) {
    return `${cleanNip.slice(0, 3)}-${cleanNip.slice(3, 6)}-${cleanNip.slice(6, 8)}-${cleanNip.slice(8, 10)}`;
  }
  
  return nip;
};

// REGON validation
export const validateREGON = (regon: string): boolean => {
  const cleanRegon = regon.replace(/[^0-9]/g, '');
  
  if (cleanRegon.length === 9) {
    return validateREGON9(cleanRegon);
  } else if (cleanRegon.length === 14) {
    return validateREGON14(cleanRegon);
  }
  
  return false;
};

const validateREGON9 = (regon: string): boolean => {
  if (regon === '000000000') return false;
  
  const weights = [8, 9, 2, 3, 4, 5, 6, 7];
  let sum = 0;
  
  for (let i = 0; i < 8; i++) {
    sum += parseInt(regon[i]) * weights[i];
  }
  
  const checksum = sum % 11;
  const lastDigit = parseInt(regon[8]);
  
  return checksum === 10 ? 0 === lastDigit : checksum === lastDigit;
};

const validateREGON14 = (regon: string): boolean => {
  if (regon === '00000000000000') return false;
  
  // First validate the 9-digit part
  if (!validateREGON9(regon.slice(0, 9))) {
    return false;
  }
  
  const weights = [2, 4, 8, 5, 0, 9, 7, 3, 6, 1, 2, 4, 8];
  let sum = 0;
  
  for (let i = 0; i < 13; i++) {
    sum += parseInt(regon[i]) * weights[i];
  }
  
  const checksum = sum % 11;
  const lastDigit = parseInt(regon[13]);
  
  return checksum === 10 ? 0 === lastDigit : checksum === lastDigit;
};

// Polish date formatting
export const formatPolishDate = (date: Date, format: string = 'DD.MM.YYYY'): string => {
  const day = date.getDate().toString().padStart(2, '0');
  const month = (date.getMonth() + 1).toString().padStart(2, '0');
  const year = date.getFullYear().toString();
  
  const polishMonths = [
    'stycznia', 'lutego', 'marca', 'kwietnia', 'maja', 'czerwca',
    'lipca', 'sierpnia', 'września', 'października', 'listopada', 'grudnia'
  ];
  
  return format
    .replace('DD', day)
    .replace('MM', month)
    .replace('MMMM', polishMonths[date.getMonth()])
    .replace('YYYY', year);
};

// Parse Polish date string
export const parsePolishDate = (dateString: string, format: string = 'DD.MM.YYYY'): Date | null => {
  const parts = dateString.split(/[.\-\/]/);
  
  if (parts.length !== 3) {
    return null;
  }
  
  const day = parseInt(parts[0]);
  const month = parseInt(parts[1]) - 1; // Month is 0-indexed
  const year = parseInt(parts[2]);
  
  if (isNaN(day) || isNaN(month) || isNaN(year)) {
    return null;
  }
  
  const date = new Date(year, month, day);
  
  // Validate that the date is valid
  if (date.getDate() !== day || date.getMonth() !== month || date.getFullYear() !== year) {
    return null;
  }
  
  return date;
};

// Polish VAT rates
export const getPolishVATRates = (): number[] => {
  return [0, 5, 8, 23];
};

// Calculate Polish VAT
export const calculatePolishVAT = (netAmount: number, vatRate: number) => {
  const vat = Math.round((netAmount * vatRate / 100) * 100) / 100;
  const gross = Math.round((netAmount + vat) * 100) / 100;
  
  return {
    net: netAmount,
    vat: vat,
    gross: gross,
  };
};

// Polish business day validation
export const isPolishBusinessDay = (date: Date): boolean => {
  const day = date.getDay();
  
  // Check if it's weekend
  if (day === 0 || day === 6) {
    return false;
  }
  
  // Check if it's a Polish holiday
  return !isPolishHoliday(date);
};

// Polish holiday validation
export const isPolishHoliday = (date: Date): boolean => {
  const month = date.getMonth();
  const day = date.getDate();
  const year = date.getFullYear();
  
  // Fixed holidays
  const fixedHolidays = [
    { month: 0, day: 1 },   // New Year's Day
    { month: 0, day: 6 },   // Epiphany
    { month: 4, day: 1 },   // Labour Day
    { month: 4, day: 3 },   // Constitution Day
    { month: 7, day: 15 },  // Assumption of Mary
    { month: 10, day: 1 },  // All Saints' Day
    { month: 10, day: 11 }, // Independence Day
    { month: 11, day: 25 }, // Christmas Day
    { month: 11, day: 26 }, // Boxing Day
  ];
  
  // Check fixed holidays
  if (fixedHolidays.some(holiday => holiday.month === month && holiday.day === day)) {
    return true;
  }
  
  // Calculate Easter and related holidays
  const easter = calculateEaster(year);
  const easterMonth = easter.getMonth();
  const easterDay = easter.getDate();
  
  // Easter Monday (day after Easter)
  const easterMonday = new Date(easter);
  easterMonday.setDate(easterMonday.getDate() + 1);
  
  // Corpus Christi (60 days after Easter)
  const corpusChristi = new Date(easter);
  corpusChristi.setDate(corpusChristi.getDate() + 60);
  
  if ((month === easterMonday.getMonth() && day === easterMonday.getDate()) ||
      (month === corpusChristi.getMonth() && day === corpusChristi.getDate())) {
    return true;
  }
  
  return false;
};

// Calculate Easter date for a given year
const calculateEaster = (year: number): Date => {
  const a = year % 19;
  const b = Math.floor(year / 100);
  const c = year % 100;
  const d = Math.floor(b / 4);
  const e = b % 4;
  const f = Math.floor((b + 8) / 25);
  const g = Math.floor((b - f + 1) / 3);
  const h = (19 * a + b - d - g + 15) % 30;
  const i = Math.floor(c / 4);
  const k = c % 4;
  const l = (32 + 2 * e + 2 * i - h - k) % 7;
  const m = Math.floor((a + 11 * h + 22 * l) / 451);
  const month = Math.floor((h + l - 7 * m + 114) / 31) - 1; // 0-indexed month
  const day = ((h + l - 7 * m + 114) % 31) + 1;
  
  return new Date(year, month, day);
};

// Polish invoice number validation
export const validatePolishInvoiceNumber = (invoiceNumber: string): boolean => {
  // Polish invoice numbers typically follow patterns like:
  // FV/2024/001, INV-2024-001, 001/03/2024, etc.
  const patterns = [
    /^[A-Z]{1,4}\/\d{4}\/\d{1,6}$/, // FV/2024/001
    /^[A-Z]{1,4}-\d{4}-\d{1,6}$/, // INV-2024-001
    /^\d{1,6}\/\d{1,2}\/\d{4}$/, // 001/03/2024
    /^\d{1,6}\/\d{4}$/, // 001/2024
  ];
  
  return patterns.some(pattern => pattern.test(invoiceNumber));
};

// Format Polish phone number
export const formatPolishPhoneNumber = (phone: string): string => {
  const cleanPhone = phone.replace(/[^0-9]/g, '');
  
  if (cleanPhone.length === 9) {
    // Mobile number format: 123 456 789
    return `${cleanPhone.slice(0, 3)} ${cleanPhone.slice(3, 6)} ${cleanPhone.slice(6, 9)}`;
  } else if (cleanPhone.length === 11 && cleanPhone.startsWith('48')) {
    // International format: +48 123 456 789
    return `+48 ${cleanPhone.slice(2, 5)} ${cleanPhone.slice(5, 8)} ${cleanPhone.slice(8, 11)}`;
  }
  
  return phone;
};

// Validate Polish postal code
export const validatePolishPostalCode = (postalCode: string): boolean => {
  const pattern = /^\d{2}-\d{3}$/;
  return pattern.test(postalCode);
};

// Format Polish postal code
export const formatPolishPostalCode = (postalCode: string): string => {
  const cleanCode = postalCode.replace(/[^0-9]/g, '');
  
  if (cleanCode.length === 5) {
    return `${cleanCode.slice(0, 2)}-${cleanCode.slice(2, 5)}`;
  }
  
  return postalCode;
};

// Polish business entity types
export const getPolishBusinessEntityTypes = () => {
  return [
    { value: 'jednoosobowa_dzialalnosc', label: 'Jednoosobowa działalność gospodarcza' },
    { value: 'spolka_cywilna', label: 'Spółka cywilna' },
    { value: 'spolka_jawna', label: 'Spółka jawna' },
    { value: 'spolka_partnerska', label: 'Spółka partnerska' },
    { value: 'spolka_komandytowa', label: 'Spółka komandytowa' },
    { value: 'spolka_z_oo', label: 'Spółka z ograniczoną odpowiedzialnością' },
    { value: 'spolka_akcyjna', label: 'Spółka akcyjna' },
  ];
};

// Polish accounting periods
export const getPolishAccountingPeriods = () => {
  return [
    { value: 'monthly', label: 'Miesięczny' },
    { value: 'quarterly', label: 'Kwartalny' },
    { value: 'yearly', label: 'Roczny' },
  ];
};

// Polish tax office codes
export const getPolishTaxOfficeCodes = () => {
  return [
    { value: '1471', label: 'Urząd Skarbowy Warszawa-Śródmieście' },
    { value: '1472', label: 'Urząd Skarbowy Warszawa-Mokotów' },
    { value: '1473', label: 'Urząd Skarbowy Warszawa-Wola' },
    // Add more tax offices as needed
  ];
};