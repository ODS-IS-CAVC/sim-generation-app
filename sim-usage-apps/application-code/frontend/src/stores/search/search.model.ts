export interface GridSearch {
  happenTime: string;
  nearmissType: Array<string>;
}

export interface PageControl {
  page: number;
}
export interface itemsPerPageControl {
  itemsPerPage: number;
}

export interface selectSectionRow {
  sectionId: string;
  sectionName: string;
}

export interface selectLocationRow {
  locationId: string;
  locationName: string;
}
export interface SearchControl
  extends GridSearch,
    PageControl,
    itemsPerPageControl,
    selectSectionRow,
    selectLocationRow {}
