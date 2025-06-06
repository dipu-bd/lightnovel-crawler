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
  const [filtered, setFiltered] = useState(sources);

  // Get unique language codes for the dropdown
  const languages = useMemo(
    () => Array.from(new Set(sources.map((x) => x.language))).sort(),
    [sources]
  );

  // Filter logic
  const applyFilter = (filter: SourceFilterState) => {
    const filtered = sources.filter((src) => {
      if (
        filter.search &&
        !src.domain.toLowerCase().includes(filter.search.toLowerCase())
      ) {
        return false;
      }
      if (filter.language && src.language !== filter.language) {
        return false;
      }
      for (const feature of filter.features) {
        if (!(src as any)[feature]) return false;
      }
      return true;
    });
    setFiltered(filtered);
  };

  return (
    <List
      size="small"
      dataSource={filtered}
      grid={{ gutter: 5, column: 1 }}
      header={
        <SupportedSourceFilter onChange={applyFilter} languages={languages} />
      }
      renderItem={(source) => (
        <List.Item style={{ margin: 0, marginTop: 5, padding: 0 }}>
          <SupportedSourceItem source={source} disabled={disabled} />
        </List.Item>
      )}
    />
  );
};
