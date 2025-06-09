import { type Chapter, type Volume } from '@/types';
import { Card, Collapse, List } from 'antd';
import qs from 'qs';
import { Link } from 'react-router-dom';

export const NovelTableOfContentsCard: React.FC<{
  toc: Volume[];
}> = ({ toc }) => {
  return (
    <Card title="Table of Contents">
      <Collapse
        items={toc.map((volume) => ({
          key: String(volume.id),
          label: volume.title,
          children: <NovelChapterList volume={volume} />,
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
      split={false}
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
    <List.Item>
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
