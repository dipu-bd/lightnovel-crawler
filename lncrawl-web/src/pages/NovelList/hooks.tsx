import type { Novel, PaginatiedResponse } from '@/types';
import { stringifyError } from '@/utils/errors';
import { Grid } from 'antd';
import axios from 'axios';
import { useCallback, useEffect, useMemo, useState } from 'react';
import { useSearchParams } from 'react-router-dom';

export function useNovelList() {
  const breakpoint = Grid.useBreakpoint();
  const [searchParams, setSearchParams] = useSearchParams();

  const [refreshId, setRefreshId] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>();

  const [total, setTotal] = useState(0);
  const [novels, setNovels] = useState<Novel[]>([]);

  const currentPage = useMemo(
    () => parseInt(searchParams.get('page') || '1', 10),
    [searchParams]
  );

  const perPage = useMemo(() => {
    //  xs={12} sm={8} lg={6} xl={4}
    if (breakpoint.xl) return 18;
    if (breakpoint.lg) return 12;
    if (breakpoint.sm) return 12;
    return 8;
  }, [breakpoint.xl, breakpoint.lg, breakpoint.sm]);

  const fetchNovels = async (page: number, limit: number) => {
    setError(undefined);
    try {
      const offset = (page - 1) * limit;
      const { data } = await axios.get<PaginatiedResponse<Novel>>(
        '/api/novels',
        {
          params: { offset, limit },
        }
      );
      setTotal(data.total);
      setNovels(data.items);
    } catch (err: any) {
      setError(stringifyError(err));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const tid = setTimeout(() => {
      fetchNovels(currentPage, perPage);
    }, 50);
    return () => clearTimeout(tid);
  }, [currentPage, perPage, refreshId]);

  const refresh = useCallback(() => {
    setLoading(true);
    setRefreshId((v) => v + 1);
  }, []);

  const changePage = useCallback(
    (page: number) => {
      setSearchParams({ page: String(page) });
    },
    [setSearchParams]
  );

  return {
    perPage,
    currentPage,
    novels,
    total,
    loading,
    error,
    refresh,
    changePage,
  };
}
