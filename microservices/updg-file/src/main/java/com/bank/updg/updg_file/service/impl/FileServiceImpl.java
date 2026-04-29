package com.bank.updg.updg_file.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.bank.updg.common.exception.BusinessException;
import com.bank.updg.common.model.enums.ErrorCodeEnum;
import com.bank.updg.updg_file.mapper.FileInfoMapper;
import com.bank.updg.updg_file.model.entity.FileInfo;
import com.bank.updg.updg_file.service.FileService;
import io.minio.GetObjectArgs;
import io.minio.GetPresignedObjectUrlArgs;
import io.minio.MinioClient;
import io.minio.PutObjectArgs;
import io.minio.RemoveObjectArgs;
import io.minio.http.Method;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.io.InputStream;
import java.time.LocalDateTime;
import java.util.UUID;

@Slf4j
@Service
@RequiredArgsConstructor
public class FileServiceImpl implements FileService {

    private final FileInfoMapper fileInfoMapper;
    private final MinioClient minioClient;

    @Value("${minio.bucket:updg-files}")
    private String defaultBucket;

    @Override
    public FileInfo uploadFile(InputStream input, String fileName, String contentType, Long size,
                               String uploadedBy, String projectId, String category) {
        String fileId = UUID.randomUUID().toString().replace("-", "");
        String objectKey = projectId != null
                ? projectId + "/" + fileId + "_" + fileName
                : fileId + "_" + fileName;

        // TODO: Ensure bucket exists; create if not present
        // minioClient.makeBucket(MakeBucketArgs.builder().bucket(defaultBucket).build());

        try {
            // Upload to MinIO
            minioClient.putObject(PutObjectArgs.builder()
                    .bucket(defaultBucket)
                    .object(objectKey)
                    .stream(input, size, -1)
                    .contentType(contentType != null ? contentType : "application/octet-stream")
                    .build());

            // Save metadata to DB
            FileInfo info = FileInfo.builder()
                    .fileId(fileId)
                    .fileName(fileName)
                    .originalName(fileName)
                    .contentType(contentType)
                    .fileSize(size)
                    .bucket(defaultBucket)
                    .objectKey(objectKey)
                    .uploadedBy(uploadedBy)
                    .projectId(projectId)
                    .category(category)
                    .createTime(LocalDateTime.now())
                    .updateTime(LocalDateTime.now())
                    .build();

            fileInfoMapper.insert(info);
            return info;

        } catch (Exception e) {
            log.error("Failed to upload file: {}", fileName, e);
            throw new BusinessException(ErrorCodeEnum.SYSTEM_ERROR, "File upload failed: " + e.getMessage());
        }
    }

    @Override
    public InputStream downloadFile(String fileId) {
        FileInfo info = getFileInfo(fileId);
        try {
            return minioClient.getObject(GetObjectArgs.builder()
                    .bucket(info.getBucket())
                    .object(info.getObjectKey())
                    .build());
        } catch (Exception e) {
            log.error("Failed to download file: {}", fileId, e);
            throw new BusinessException(ErrorCodeEnum.SYSTEM_ERROR, "File download failed: " + e.getMessage());
        }
    }

    @Override
    public FileInfo getFileInfo(String fileId) {
        FileInfo info = fileInfoMapper.selectById(fileId);
        if (info == null) {
            throw new BusinessException(ErrorCodeEnum.FILE_NOT_FOUND);
        }
        return info;
    }

    @Override
    public Page<FileInfo> listFiles(String projectId, String category, int page, int size) {
        Page<FileInfo> pageObj = new Page<>(page, size);
        LambdaQueryWrapper<FileInfo> wrapper = new LambdaQueryWrapper<>();

        if (projectId != null && !projectId.isBlank()) {
            wrapper.eq(FileInfo::getProjectId, projectId);
        }
        if (category != null && !category.isBlank()) {
            wrapper.eq(FileInfo::getCategory, category);
        }
        wrapper.orderByDesc(FileInfo::getCreateTime);

        return fileInfoMapper.selectPage(pageObj, wrapper);
    }

    @Override
    public void deleteFile(String fileId, String userId) {
        FileInfo info = getFileInfo(fileId);

        // TODO: verify userId matches uploadedBy or has admin permission
        try {
            // Remove from MinIO
            minioClient.removeObject(RemoveObjectArgs.builder()
                    .bucket(info.getBucket())
                    .object(info.getObjectKey())
                    .build());

            // Remove metadata from DB
            fileInfoMapper.deleteById(fileId);

        } catch (Exception e) {
            log.error("Failed to delete file: {}", fileId, e);
            throw new BusinessException(ErrorCodeEnum.SYSTEM_ERROR, "File deletion failed: " + e.getMessage());
        }
    }

    @Override
    public String previewUrl(String fileId) {
        FileInfo info = getFileInfo(fileId);
        try {
            // Generate presigned URL valid for 1 hour
            return minioClient.getPresignedObjectUrl(GetPresignedObjectUrlArgs.builder()
                    .bucket(info.getBucket())
                    .object(info.getObjectKey())
                    .method(Method.GET)
                    .expiry(3600)
                    .build());
        } catch (Exception e) {
            log.error("Failed to generate preview URL for file: {}", fileId, e);
            throw new BusinessException(ErrorCodeEnum.SYSTEM_ERROR, "Preview URL generation failed: " + e.getMessage());
        }
    }
}
