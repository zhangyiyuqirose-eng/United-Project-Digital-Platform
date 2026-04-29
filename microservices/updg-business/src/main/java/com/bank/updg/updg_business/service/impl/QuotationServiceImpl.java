package com.bank.updg.updg_business.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.bank.updg.updg_business.mapper.QuotationMapper;
import com.bank.updg.updg_business.model.entity.Quotation;
import com.bank.updg.updg_business.service.QuotationService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class QuotationServiceImpl extends ServiceImpl<QuotationMapper, Quotation>
        implements QuotationService {

    @Override
    public Quotation createQuotation(Quotation data) {
        if (data.getQuotationId() == null || data.getQuotationId().isEmpty()) {
            data.setQuotationId(UUID.randomUUID().toString());
        }
        if (data.getQuoteNumber() == null || data.getQuoteNumber().isEmpty()) {
            data.setQuoteNumber("QT-" + System.currentTimeMillis());
        }
        if (data.getStatus() == null) {
            data.setStatus("DRAFT");
        }
        String now = LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME);
        data.setCreatedAt(now);
        data.setUpdatedAt(now);
        save(data);
        return data;
    }

    @Override
    public void updateQuotation(String quotationId, Quotation data) {
        Quotation existing = getById(quotationId);
        if (existing == null) {
            throw new RuntimeException("Quotation not found: " + quotationId);
        }
        if (data.getOpportunityId() != null) existing.setOpportunityId(data.getOpportunityId());
        if (data.getProjectId() != null) existing.setProjectId(data.getProjectId());
        if (data.getTotalPrice() != null) existing.setTotalPrice(data.getTotalPrice());
        if (data.getTaxRate() != null) existing.setTaxRate(data.getTaxRate());
        if (data.getValidUntil() != null) existing.setValidUntil(data.getValidUntil());
        if (data.getItems() != null) existing.setItems(data.getItems());
        existing.setUpdatedAt(LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME));
        updateById(existing);
    }

    @Override
    public Quotation getQuotation(String quotationId) {
        return getById(quotationId);
    }

    @Override
    public Page<Quotation> listQuotations(String opportunityId, String status, int page, int size) {
        Page<Quotation> pageObj = new Page<>(page, size);
        LambdaQueryWrapper<Quotation> wrapper = new LambdaQueryWrapper<Quotation>()
                .orderByDesc(Quotation::getCreatedAt);
        if (opportunityId != null) {
            wrapper.eq(Quotation::getOpportunityId, opportunityId);
        }
        if (status != null) {
            wrapper.eq(Quotation::getStatus, status);
        }
        return page(pageObj, wrapper);
    }

    @Override
    public void sendQuotation(String quotationId) {
        Quotation q = getById(quotationId);
        if (q == null) throw new RuntimeException("Quotation not found: " + quotationId);
        q.setStatus("SENT");
        q.setUpdatedAt(LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME));
        updateById(q);
    }

    @Override
    public void acceptQuotation(String quotationId) {
        Quotation q = getById(quotationId);
        if (q == null) throw new RuntimeException("Quotation not found: " + quotationId);
        q.setStatus("ACCEPTED");
        q.setUpdatedAt(LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME));
        updateById(q);
    }

    @Override
    public void rejectQuotation(String quotationId) {
        Quotation q = getById(quotationId);
        if (q == null) throw new RuntimeException("Quotation not found: " + quotationId);
        q.setStatus("REJECTED");
        q.setUpdatedAt(LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME));
        updateById(q);
    }
}
