export interface District {
  code: string;
  name: string;
}

export const districtsByProvince: Record<string, District[]> = {
  WP: [
    { code: 'CMB', name: 'Colombo' },
    { code: 'GAM', name: 'Gampaha' },
    { code: 'KAL', name: 'Kalutara' },
  ],
  CP: [
    { code: 'KAN', name: 'Kandy' },
    { code: 'MAT', name: 'Matale' },
    { code: 'NUE', name: 'Nuwara Eliya' },
  ],
  SP: [
    { code: 'GAL', name: 'Galle' },
    { code: 'MTR', name: 'Matara' },
    { code: 'HBT', name: 'Hambantota' },
  ],
  NP: [
    { code: 'JAF', name: 'Jaffna' },
    { code: 'KIL', name: 'Kilinochchi' },
    { code: 'MAN', name: 'Mannar' },
    { code: 'MUL', name: 'Mullaitivu' },
    { code: 'VAV', name: 'Vavuniya' },
  ],
  EP: [
    { code: 'BAT', name: 'Batticaloa' },
    { code: 'AMP', name: 'Ampara' },
    { code: 'TRI', name: 'Trincomalee' },
  ],
  NW: [
    { code: 'KUR', name: 'Kurunegala' },
    { code: 'PUT', name: 'Puttalam' },
  ],
  NC: [
    { code: 'ANU', name: 'Anuradhapura' },
    { code: 'POL', name: 'Polonnaruwa' },
  ],
  UVA: [
    { code: 'BAD', name: 'Badulla' },
    { code: 'MON', name: 'Monaragala' },
  ],
  SAB: [
    { code: 'RAT', name: 'Ratnapura' },
    { code: 'KEG', name: 'Kegalle' },
  ],
};
