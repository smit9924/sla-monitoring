/** Generic server-side pagination/sort/search query, mirroring the backend's `*ListQueryParams` schemas. */
export interface PaginatedQuery<TSortBy extends string> {
  searchTerm?: string;
  pageSize: number;
  sortBy: TSortBy;
  sortDirection: 'asc' | 'desc';
  /** 1-based page number, matching the backend's `page_number`. */
  pageNumber: number;
}

/** Generic paginated listing response, mirroring the backend's `*ListResponse` schemas. */
export interface PaginatedResponse<TItem> {
  items: TItem[];
  totalCount: number;
  pageNumber: number;
  pageSize: number;
}
