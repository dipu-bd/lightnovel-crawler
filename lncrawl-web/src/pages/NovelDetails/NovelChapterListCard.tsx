import { type Chapter, type Volume } from '@/types';
import { Card, Collapse, List, Typography } from 'antd';
import qs from 'qs';
import { Link } from 'react-router-dom';

export const NovelTableOfContentsCard: React.FC<{
  toc: Volume[];
}> = ({ toc }) => {
  return (
    <Card title="Table of Contents" styles={{ body: { padding: 10 } }}>
      <Collapse
        items={toc.map((volume) => ({
          key: String(volume.id),
          label: volume.title,
          children: <NovelChapterList volume={volume} />,
          extra: (
            <Typography.Text
              type="secondary"
              style={{ fontSize: '12px', whiteSpace: 'nowrap' }}
            >
              {Intl.NumberFormat('en').format(volume.chapters.length)} chapters
            </Typography.Text>
          ),
          styles: {
            body: { padding: 0 },
            header: { opacity: volume.isRead ? 0.5 : 1 },
          },
        }))}
      />
    </Card>
  );
};

const NovelChapterList: React.FC<{
  volume: Volume;
}> = ({ volume }) => {
  return (
    <List
      size="small"
      dataSource={volume.chapters}
      renderItem={(item, index) => (
        <NovelChapterItem
          chapter={item}
          prev={volume.chapters[index - 1]}
          next={volume.chapters[index + 1]}
        />
      )}
    />
  );
};

const NovelChapterItem: React.FC<{
  chapter: Chapter;
  prev?: Chapter;
  next?: Chapter;
}> = ({ chapter, prev, next }) => {
  return (
    <List.Item style={{ opacity: chapter.isRead ? 0.5 : 1 }}>
      <Link
        to={{
          pathname: `chapter/${chapter.hash}`,
          search: qs.stringify(
            {
              prev: prev ? `chapter/${prev.hash}` : undefined,
              next: next ? `chapter/${next.hash}` : undefined,
            },
            {
              addQueryPrefix: true,
              skipNulls: true,
            }
          ),
        }}
      >
        {chapter.title}
      </Link>
    </List.Item>
  );
};
