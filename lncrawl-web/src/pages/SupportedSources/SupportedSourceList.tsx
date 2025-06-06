import type { SupportedSource } from '@/types';
import { List } from 'antd';
import { useMemo, useState } from 'react';
import {
  type SourceFilterState,
  SupportedSourceFilter,
} from './SupportedSourceFilter';
import { SupportedSourceItem } from './SupportedSourceItem';

export const SupportedSourceList: React.FC<{
  sources: SupportedSource[];
  disabled?: boolean;
}> = ({ sources, disabled }) => {
  // Filter state
  const [filter, setFilter] = useState<SourceFilterState>({
    search: '',
    language: undefined,
    has_manga: false,
    has_mtl: false,
    can_search: false,
    can_login: false,
    can_logout: false,
  });

  // Filter logic
  const filtered = useMemo(
    () =>
      sources.filter((src) => {
        if (
          filter.search &&
          !src.url.toLowerCase().includes(filter.search.toLowerCase()) &&
          !src.url
            .split('/')[2]
            .toLowerCase()
            .includes(filter.search.toLowerCase())
        ) {
          return false;
        }
        if (filter.language && src.language !== filter.language) {
          return false;
        }
        if (filter.has_manga && !src.has_manga) {
          return false;
        }
        if (filter.has_mtl && !src.has_mtl) {
          return false;
        }
        if (filter.can_search && !src.can_search) {
          return false;
        }
        if (filter.can_login && !src.can_login) {
          return false;
        }
        if (filter.can_logout && !src.can_logout) {
          return false;
        }
        return true;
      }),
    [sources, filter]
  );

  // Get unique language codes for the dropdown
  const languages = useMemo(
    () => Array.from(new Set(sources.map((x) => x.language))).sort(),
    [sources]
  );

  return (
    <List
      size="small"
      dataSource={filtered}
      grid={{ gutter: 5, column: 1 }}
      header={
        <SupportedSourceFilter
          filter={filter}
          onChange={setFilter}
          languages={languages}
        />
      }
      renderItem={(source) => (
        <List.Item style={{ margin: 0, marginTop: 5, padding: 0 }}>
          <SupportedSourceItem source={source} disabled={disabled} />
        </List.Item>
      )}
    />
  );
};
