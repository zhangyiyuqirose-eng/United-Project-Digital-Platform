package com.bank.updg.updg_resource.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.bank.updg.updg_resource.model.entity.LeaveRequest;

import java.util.List;

public interface LeaveRequestService extends IService<LeaveRequest> {

    LeaveRequest submitRequest(LeaveRequest request);

    List<LeaveRequest> getByStaffId(String staffId);

    List<LeaveRequest> getPending();

    void approveRequest(String id, String approvedBy);

    void rejectRequest(String id, String approvedBy);
}
