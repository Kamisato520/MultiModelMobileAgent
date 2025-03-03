package com.example.myapplication.adapter;

import android.content.Intent;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageView;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.cardview.widget.CardView;
import androidx.recyclerview.widget.RecyclerView;

import com.example.myapplication.R;
import com.example.myapplication.model.FunctionModule;

import java.util.List;

public class FunctionModuleAdapter extends RecyclerView.Adapter<FunctionModuleAdapter.ViewHolder> {
    private List<FunctionModule> modules;

    public FunctionModuleAdapter(List<FunctionModule> modules) {
        this.modules = modules;
    }

    public static class ViewHolder extends RecyclerView.ViewHolder {
        public CardView cardView;
        public ImageView iconView;
        public TextView nameView;
        public TextView descriptionView;

        public ViewHolder(View view) {
            super(view);
            cardView = view.findViewById(R.id.module_card);
            iconView = view.findViewById(R.id.module_icon);
            nameView = view.findViewById(R.id.module_name);
            descriptionView = view.findViewById(R.id.module_description);
        }
    }

    @NonNull
    @Override
    public ViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.item_function_module, parent, false);
        return new ViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull ViewHolder holder, int position) {
        FunctionModule module = modules.get(position);
        holder.iconView.setImageResource(module.getIconResId());
        holder.nameView.setText(module.getName());
        holder.descriptionView.setText(module.getDescription());
        holder.cardView.setCardBackgroundColor(module.getBackgroundColor());
        
        holder.cardView.setOnClickListener(v -> {
            Intent intent = new Intent(v.getContext(), module.getTargetActivity());
            v.getContext().startActivity(intent);
        });
    }

    @Override
    public int getItemCount() {
        return modules.size();
    }
} 