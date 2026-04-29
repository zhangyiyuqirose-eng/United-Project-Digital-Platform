package com.bank.updg.updg_resource.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.bank.updg.updg_resource.mapper.LeaveRequestMapper;
import com.bank.updg.updg_resource.model.entity.LeaveRequest;
import com.bank.updg.updg_resource.service.LeaveRequestService;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;

@Service
public class LeaveRequestServiceImpl
        extends ServiceImpl<LeaveRequestMapper, LeaveRequest>
        implements LeaveRequestService {

    @Override
    public LeaveRequest submitRequest(LeaveRequest request) {
        request.setId(UUID.randomUUID().toString().replace("-", ""));
        request.setStatus("PENDING");
        save(request);
        return request;
    }

    @Override
    public List<LeaveRequest> getByStaffId(String staffId) {
        LambdaQueryWrapper<LeaveRequest> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(LeaveRequest::getStaffId, staffId);
        return list(wrapper);
    }

    @Override
    public List<LeaveRequest> getPending() {
        LambdaQueryWrapper<LeaveRequest> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(LeaveRequest::getStatus, "PENDING");
        return list(wrapper);
    }

    @Override
    public void approveRequest(String id, String approvedBy) {
        LeaveRequest request = getById(id);
        if (request != null) {
            request.setStatus("APPROVED");
            request.setApprovedBy(approvedBy);
            request.setApprovedAt(LocalDateTime.now());
            updateById(request);
        }
    }

    @Override
    public void rejectRequest(String id, String approvedBy) {
        LeaveRequest request = getById(id);
        if (request != null) {
            request.setStatus("REJECTED");
            request.setApprovedBy(approvedBy);
            request.setApprovedAt(LocalDateTime.now());
            updateById(request);
        }
    }
}
